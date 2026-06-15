"""Deterministic semantic-aware grading for curated answer diagnostics."""

from __future__ import annotations

import json
import re
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.ratings import letter_to_grade_band, score_to_letter
from aws_certification_coach.training.dataset import load_feedback_regression_examples


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
    curated_path: Path,
    questions_by_id: dict[str, Question],
) -> dict[str, object]:
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    examples = load_feedback_regression_examples(curated_path, questions_by_id)
    matches = 0
    mismatches = []
    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        question = questions_by_id[example.question_id]
        score = semantic_similarity_score(question, example.answer)
        actual = score_to_letter(score)
        expected = str(row["correct_rating"]).strip().upper()
        actual_band = letter_to_grade_band(actual)
        expected_band = letter_to_grade_band(expected)
        if actual_band == expected_band:
            matches += 1
            continue
        mismatches.append(
            {
                "row": index,
                "question_id": example.question_id,
                "answer": example.answer,
                "expected": expected,
                "actual": actual,
                "expected_band": expected_band,
                "actual_band": actual_band,
                "score": score,
            }
        )
    total = len(examples)
    return {
        "semantic_grade_accuracy": matches / max(1, total),
        "semantic_matching_grade_bands": matches,
        "semantic_example_count": total,
        "semantic_mismatches": mismatches,
    }


def semantic_similarity_score(question: Question, answer: str) -> int:
    """Score an answer using service-alias recognition plus concept coverage."""

    if _matches_incorrect_option(question, answer):
        return 35

    answer_tokens = set(_tokens(answer))
    content_tokens = answer_tokens - GENERIC_TOKENS
    concept_coverage = _concept_coverage(question, answer)
    if _service_is_covered(question, answer):
        return round(80 + (15 * concept_coverage))

    reference_tokens = set(_tokens(question.reference_answer)) - GENERIC_TOKENS
    answer_reference_overlap = len(content_tokens & reference_tokens) / max(1, len(content_tokens))
    if concept_coverage >= 0.5:
        return round(63 + (18 * concept_coverage))
    if concept_coverage > 0 or answer_reference_overlap >= 0.5:
        return 65 if "aws" in answer_tokens or answer_reference_overlap >= 0.5 else 62
    if content_tokens & reference_tokens:
        return 58
    return 25


def _service_is_covered(question: Question, answer: str) -> bool:
    normalized_answer = _normalized(answer)
    return any(alias in normalized_answer for alias in _service_aliases(question))


def _service_aliases(question: Question) -> set[str]:
    correct_options, _incorrect_options = _option_texts(question)
    values = {_strip_leading_use(option) for option in correct_options}
    values.add(_strip_leading_use(question.reference_answer.split(" to ")[0]))
    if question.key_concepts:
        values.add(_normalized(question.key_concepts[0]))

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
    for concept in question.key_concepts:
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
        if len(concept_token_set & answer_tokens) / len(concept_token_set) >= 0.5:
            covered += 1
    return covered / max(1, len(question.key_concepts))


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
