"""Deterministic semantic_similarity grading for curated answer diagnostics."""

from __future__ import annotations

import json
import re
from pathlib import Path
from collections.abc import Iterable

from aws_certification_coach.domain import Question
from aws_certification_coach.ratings import letter_to_grade_band, letter_to_numeric, score_to_letter
from aws_certification_coach.training.dataset import load_feedback_regression_examples
from aws_certification_coach.training.features import correct_answer_text


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
GENERIC_TOKENS = {
    "amazon",
    "and",
    "aws",
    "classes",
    "data",
    "feature",
    "for",
    "managed",
    "manager",
    "service",
    "the",
    "to",
    "use",
}
SERVICE_FAMILY_TOKENS = {
    "dynamodb",
    "ec2",
    "iam",
    "kinesis",
    "lambda",
    "rds",
    "s3",
    "vpc",
}
AMBIGUOUS_ALIAS_TOKENS = {
    "allow",
    "amazon",
    "aws",
    "data",
    "deny",
    "feature",
    "route",
    "rules",
    "s3",
    "service",
}


def evaluate_semantic_curated_answers(
    curated_path: Path | Iterable[Path],
    questions: list[Question],
) -> dict[str, object]:
    grade_band_matches = 0
    exact_letter_matches = 0
    true_positive = false_positive = true_negative = false_negative = 0
    mismatches = []
    rows_and_examples = _feedback_rows_and_examples(curated_path, questions)
    for index, (source_path, source_row, row, example) in enumerate(rows_and_examples):
        question = example.question
        score = semantic_similarity_score(question, example.answer)
        actual = score_to_letter(score)
        expected = str(row["correct_rating"]).strip().upper()
        expected_accept = expected != "F"
        actual_accept = actual != "F"
        true_positive += int(expected_accept and actual_accept)
        false_positive += int(not expected_accept and actual_accept)
        true_negative += int(not expected_accept and not actual_accept)
        false_negative += int(expected_accept and not actual_accept)
        expected_grade_band = letter_to_grade_band(expected)
        actual_grade_band = letter_to_grade_band(actual)
        if actual_grade_band == expected_grade_band:
            grade_band_matches += 1
        if actual == expected:
            exact_letter_matches += 1
            continue
        mismatches.append(
            {
                "row": index,
                "source": str(source_path),
                "source_row": source_row,
                "question": question.question,
                "user_answer": example.answer,
                "correct_answer": correct_answer_text(question),
                "expected_rating": letter_to_numeric(expected),
                "expected_letter": expected,
                "actual_letter": actual,
                "score": score,
            }
        )
    total = len(rows_and_examples)
    return {
        "semantic_grade_accuracy": grade_band_matches / max(1, total),
        "semantic_exact_letter_accuracy": exact_letter_matches / max(1, total),
        "semantic_precision": true_positive / max(1, true_positive + false_positive),
        "semantic_recall": true_positive / max(1, true_positive + false_negative),
        "semantic_matching_grade_bands": grade_band_matches,
        "semantic_matching_letter_grades": exact_letter_matches,
        "semantic_example_count": total,
        "semantic_grade_scale": ["A", "B", "C", "D", "F"],
        "semantic_true_positive": true_positive,
        "semantic_false_positive": false_positive,
        "semantic_true_negative": true_negative,
        "semantic_false_negative": false_negative,
        "semantic_mismatches": mismatches,
    }


def _feedback_rows_and_examples(
    curated_path: Path | Iterable[Path],
    questions: list[Question],
) -> list[tuple[Path, int, dict, object]]:
    paths = [curated_path] if isinstance(curated_path, Path) else list(curated_path)
    rows_and_examples = []
    for path in paths:
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"Curated feedback must be a JSON list: {path}")
        examples = load_feedback_regression_examples(path, questions)
        rows_and_examples.extend(
            (path, row_index, row, example)
            for row_index, (row, example) in enumerate(zip(rows, examples, strict=True))
            if isinstance(row, dict)
        )
    return rows_and_examples


def semantic_similarity_score(question: Question, answer: str) -> int:
    """Score an answer using service-alias recognition plus concept coverage."""

    if _matches_near_miss_option(question, answer):
        return 65

    if _matches_incorrect_option(question, answer):
        return 35

    if _rephrases_question_without_answer(question, answer):
        return 65

    answer_tokens = set(_tokens(answer))
    content_tokens = answer_tokens - GENERIC_TOKENS
    concept_coverage = _concept_coverage(question, answer)
    if _has_adjacent_domain_signal(question, answer):
        concept_coverage = max(concept_coverage, 0.25)
    if _service_is_covered(question, answer):
        return round(80 + (15 * concept_coverage))

    reference_tokens = set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
    if concept_coverage >= 0.5:
        return round(63 + (18 * concept_coverage))
    if concept_coverage > 0 or _meaningful_reference_overlap(content_tokens, reference_tokens):
        return 65 if "aws" in answer_tokens or _meaningful_reference_overlap(content_tokens, reference_tokens) else 62
    if content_tokens & reference_tokens:
        return 58
    return 25


def _rephrases_question_without_answer(question: Question, answer: str) -> bool:
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if len(answer_tokens) < 4:
        return False
    normalized_answer = _normalized(answer)
    if not normalized_answer.startswith(("which ", "what ", "how ", "why ", "when ", "where ")):
        return False
    question_tokens = set(_tokens(question.question)) - GENERIC_TOKENS
    question_overlap = len(answer_tokens & question_tokens) / max(1, len(answer_tokens))
    if question_overlap < 0.5:
        return False

    reference_tokens = set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
    answer_specific_tokens = reference_tokens - question_tokens
    if not answer_specific_tokens:
        return True
    return len(answer_tokens & answer_specific_tokens) / len(answer_specific_tokens) < 0.5


def _service_is_covered(question: Question, answer: str) -> bool:
    normalized_answer = _normalized(answer)
    return any(alias in normalized_answer for alias in _service_aliases(question))


def _service_aliases(question: Question) -> set[str]:
    correct_options, _incorrect_options = _option_texts(question)
    values = {_strip_leading_use(option) for option in correct_options}
    values.add(_strip_leading_use(correct_answer_text(question)))
    concepts = _required_concepts(question)
    if concepts:
        values.add(_normalized(concepts[0]))

    aliases: set[str] = set()
    for value in values:
        if not value:
            continue
        aliases.add(value)
        distinctive_tokens = [
            token
            for token in value.split()
            if token not in GENERIC_TOKENS
        ]
        if len(distinctive_tokens) > 1:
            aliases.add(" ".join(distinctive_tokens))
        aliases.update(
            token
            for token in distinctive_tokens
            if token not in AMBIGUOUS_ALIAS_TOKENS and len(token) > 2
        )
    return {alias for alias in aliases if alias}


def _concept_coverage(question: Question, answer: str) -> float:
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer))
    covered = 0
    required_concepts = _required_concepts(question)
    for concept in required_concepts:
        concept_tokens = [
            token
            for token in _tokens(concept)
            if token not in GENERIC_TOKENS
        ]
        if not concept_tokens:
            continue
        concept_token_set = set(concept_tokens)
        if " ".join(concept_tokens) in normalized_answer:
            covered += 1
            continue
        matched_tokens = concept_token_set & answer_tokens
        if len(matched_tokens) / len(concept_token_set) >= 0.5:
            if matched_tokens <= SERVICE_FAMILY_TOKENS:
                continue
            if len(concept_token_set) > 1 and len(matched_tokens) < 2:
                continue
            covered += 1
    return covered / max(1, len(required_concepts))


def _required_concepts(question: Question) -> list[str]:
    return question.required_concepts or question.key_concepts


def _matches_near_miss_option(question: Question, answer: str) -> bool:
    _correct_options, incorrect_options = _option_texts(question)
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if not answer_tokens:
        return False
    for option in incorrect_options:
        option_tokens = set(_tokens(option)) - GENERIC_TOKENS
        if not {"alone", "only"} & option_tokens:
            continue
        normalized_option = _normalized(option)
        if normalized_answer in {normalized_option, _strip_leading_use(option)} or answer_tokens <= option_tokens:
            return _has_adjacent_domain_signal(question, answer) or bool(
                answer_tokens & set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
            )
    return False


def _matches_incorrect_option(question: Question, answer: str) -> bool:
    _correct_options, incorrect_options = _option_texts(question)
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if not answer_tokens:
        return False
    for option in incorrect_options:
        option_tokens = set(_tokens(option)) - GENERIC_TOKENS - {"only"}
        if answer_tokens <= option_tokens:
            return True
        if normalized_answer in {_normalized(option), _strip_leading_use(option)}:
            return True
    return False


def _has_adjacent_domain_signal(question: Question, answer: str) -> bool:
    question_tokens = set(_tokens(question.question))
    reference_tokens = set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if {"permissions", "permission"} & question_tokens and {"role", "roles", "iam"} & answer_tokens:
        return True
    if {"secret", "secrets", "credential", "credentials", "password", "passwords"} & question_tokens:
        return bool({"key", "keys", "kms", "parameter", "store"} & answer_tokens)
    if {"orchestrate", "orchestrates", "orchestration", "workflow", "workflows"} & question_tokens:
        return bool({"orchestrate", "orchestration", "workflow", "workflows"} & answer_tokens)
    return bool((answer_tokens & reference_tokens) - SERVICE_FAMILY_TOKENS)


def _meaningful_reference_overlap(answer_tokens: set[str], reference_tokens: set[str]) -> bool:
    overlap = answer_tokens & reference_tokens
    if not overlap:
        return False
    if overlap <= SERVICE_FAMILY_TOKENS:
        return False
    return len(overlap) / max(1, len(answer_tokens)) >= 0.5


def _option_texts(question: Question) -> tuple[list[str], list[str]]:
    original = question.original_multiple_choice
    if original is None:
        return [], []
    correct_ids = set(original.correct_option_ids)
    correct = [option.text for option in original.options if option.option_id in correct_ids]
    incorrect = [option.text for option in original.options if option.option_id not in correct_ids]
    return correct, incorrect


def _strip_leading_use(value: str) -> str:
    return re.sub(r"^use ", "", _normalized(value)).strip()


def _normalized(value: str) -> str:
    return " ".join(_tokens(value))


def _tokens(value: str) -> list[str]:
    return TOKEN_PATTERN.findall(value.casefold())
