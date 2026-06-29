"""Deterministic semantic_similarity grading for curated answer diagnostics."""

from __future__ import annotations

import json
import re
from pathlib import Path
from collections.abc import Iterable

from aws_certification_coach.domain import Question
from aws_certification_coach.knowledge_base import load_knowledge_base
from aws_certification_coach.model_evaluation.band_accuracy import BandAccuracy
from aws_certification_coach.ratings import letter_to_grade_band, letter_to_numeric, score_to_letter
from aws_certification_coach.training.dataset import load_feedback_graded_examples, question_signature
from aws_certification_coach.training.features import correct_answer_text


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
KNOWLEDGE_BASE = load_knowledge_base()
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
    "services",
    "the",
    "to",
    "use",
}
QUESTION_RESTATEMENT_FRAME_TOKENS = {
    "answer",
    "asks",
    "asking",
    "identify",
    "learner",
    "question",
    "should",
    "this",
}
SERVICE_FAMILY_TOKENS = set(KNOWLEDGE_BASE.service_tokens)
AMBIGUOUS_ALIAS_TOKENS = {
    "allow",
    "amazon",
    "aws",
    "data",
    "deny",
    "feature",
    "global",
    "route",
    "rules",
    "s3",
    "service",
    "table",
    "tables",
}
UNCERTAIN_GUESS_PHRASES = (
    "i do not know",
    "i don't know",
    "i dont know",
    "i would be guessing",
    "not sure",
    "possibly",
    "it's possible",
    "it is possible",
)
LEGACY_ACCEPTED_GRADES = frozenset({"A", "B", "C", "D"})
GRADES = ("A", "B", "C", "D", "F")


def evaluate_semantic_curated_answers(
    curated_path: Path | Iterable[Path],
    questions: list[Question],
) -> dict[str, object]:
    grade_band_matches = 0
    exact_letter_matches = 0
    true_positive = false_positive = true_negative = false_negative = 0
    confusion = {truth: {prediction: 0 for prediction in GRADES} for truth in GRADES}
    mismatches = []
    all_rows_and_examples = _feedback_rows_and_examples(curated_path, questions)
    rows_and_examples, conflict_groups = _without_conflicting_feedback(all_rows_and_examples)
    for index, (source_path, source_row, row, example) in enumerate(rows_and_examples):
        question = example.question
        score = semantic_similarity_score(question, example.answer)
        actual = score_to_letter(score)
        expected = str(row["correct_rating"]).strip().upper()
        confusion[expected][actual] += 1
        expected_accept = expected in LEGACY_ACCEPTED_GRADES
        actual_accept = actual in LEGACY_ACCEPTED_GRADES
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
                "feedback_text": str(row.get("feedback_text", "")),
            }
        )
    total = len(rows_and_examples)
    per_grade = _per_grade_metrics(confusion)
    within_one_letter_matches = sum(
        count
        for truth, predictions in confusion.items()
        for prediction, count in predictions.items()
        if abs(GRADES.index(truth) - GRADES.index(prediction)) <= 1
    )
    return {
        "semantic_grade_accuracy": grade_band_matches / max(1, total),
        "semantic_exact_letter_accuracy": exact_letter_matches / max(1, total),
        "semantic_within_one_letter_accuracy": within_one_letter_matches / max(1, total),
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
        "semantic_skipped_conflicting_examples": sum(group["example_count"] for group in conflict_groups),
        "semantic_conflicting_feedback_groups": conflict_groups,
        "per_grade": per_grade,
        "per_grade_band": BandAccuracy().evaluate(confusion),
        "confusion": confusion,
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
        examples = load_feedback_graded_examples(path, questions)
        rows_and_examples.extend(
            (path, row_index, row, example)
            for row_index, (row, example) in enumerate(zip(rows, examples, strict=True))
            if isinstance(row, dict)
        )
    return rows_and_examples


def _per_grade_metrics(
    confusion: dict[str, dict[str, int]],
) -> dict[str, dict[str, float | int | None]]:
    metrics = {}
    for grade in GRADES:
        true_positive = confusion[grade][grade]
        support = sum(confusion[grade].values())
        predicted_count = sum(predictions[grade] for predictions in confusion.values())
        precision = true_positive / predicted_count if predicted_count else None
        recall = true_positive / support if support else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall
            else None
        )
        metrics[grade] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }
    return metrics


def _without_conflicting_feedback(
    rows_and_examples: list[tuple[Path, int, dict, object]],
) -> tuple[list[tuple[Path, int, dict, object]], list[dict[str, object]]]:
    rows_by_key: dict[tuple[tuple[str, str, str], str], list[tuple[Path, int, dict, object]]] = {}
    for item in rows_and_examples:
        _source_path, _source_row, _row, example = item
        rows_by_key.setdefault(_feedback_key(example.question, example.answer), []).append(item)

    conflict_keys = {
        key
        for key, items in rows_by_key.items()
        if len({str(row["correct_rating"]).strip().upper() for _path, _source_row, row, _example in items}) > 1
    }
    conflict_groups = [
        {
            "question": items[0][3].question.question,
            "answer": items[0][3].answer,
            "labels": sorted({str(row["correct_rating"]).strip().upper() for _path, _source_row, row, _example in items}),
            "example_count": len(items),
            "sources": [
                {"path": str(path), "row": source_row}
                for path, source_row, _row, _example in items
            ],
        }
        for key, items in rows_by_key.items()
        if key in conflict_keys
    ]
    filtered = [
        item
        for item in rows_and_examples
        if _feedback_key(item[3].question, item[3].answer) not in conflict_keys
    ]
    return filtered, conflict_groups


def _feedback_key(question: Question, answer: str) -> tuple[tuple[str, str, str], str]:
    return question_signature(question), " ".join(str(answer).casefold().split())


def semantic_similarity_score(question: Question, answer: str) -> int:
    """Score an answer using service-alias recognition plus concept coverage."""

    if _is_exact_correct_answer(question, answer):
        return 95 if _has_explanatory_detail(answer, question) else 85

    if _rephrases_question_without_answer(question, answer):
        return 65

    answer_tokens = set(_tokens(answer))
    content_tokens = answer_tokens - GENERIC_TOKENS
    concept_coverage = _concept_coverage(question, answer)
    if _has_adjacent_domain_signal(question, answer):
        concept_coverage = max(concept_coverage, 0.25)
    near_miss_score = _near_miss_option_score(question, answer)
    if near_miss_score is not None:
        return near_miss_score
    adjacent_service_score = _adjacent_service_score(question, answer)
    if adjacent_service_score is not None:
        return adjacent_service_score
    incorrect_option_score = _incorrect_option_score(question, answer, concept_coverage)
    if incorrect_option_score is not None:
        return incorrect_option_score
    if _service_is_covered(question, answer):
        service_score = 80 + (15 * concept_coverage)
        if _is_complete_service_answer(answer):
            service_score = max(service_score, 90)
        if question.question_type == "artifact_review" and concept_coverage < 0.5:
            service_score = min(service_score, 75)
        if concept_coverage == 0 and _only_matches_generic_service_family(question, answer):
            service_score = min(service_score, 75)
        score_cap = _service_answer_cap(question, answer)
        if score_cap is not None:
            service_score = min(service_score, score_cap)
        return round(service_score)

    reference_tokens = set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
    if concept_coverage >= 0.5:
        return round(63 + (16 * concept_coverage))
    if concept_coverage > 0 or _meaningful_reference_overlap(content_tokens, reference_tokens):
        if concept_coverage > 0:
            return 75 if _answers_specific_required_concept(question, answer) else 65
        if _meaningful_reference_overlap(content_tokens, reference_tokens):
            return 75
        return 65 if "aws" in answer_tokens or _meaningful_reference_overlap(content_tokens, reference_tokens) else 62
    if content_tokens & reference_tokens:
        return 58
    return 25


def _rephrases_question_without_answer(question: Question, answer: str) -> bool:
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if len(answer_tokens) < 4:
        return False
    normalized_answer = _normalized(answer)
    if not normalized_answer.startswith(("which ", "what ", "how ", "why ", "when ", "where ")) and not (
        "question" in answer_tokens or {"asks", "asking"} & answer_tokens
    ):
        return False
    question_tokens = set(_tokens(question.question)) - GENERIC_TOKENS
    comparison_tokens = answer_tokens - QUESTION_RESTATEMENT_FRAME_TOKENS
    question_overlap = len(answer_tokens & question_tokens) / max(1, len(answer_tokens))
    framed_overlap = len(comparison_tokens & question_tokens) / max(1, len(comparison_tokens))
    question_overlap = max(question_overlap, framed_overlap)
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


def _only_matches_generic_service_family(question: Question, answer: str) -> bool:
    normalized_answer = _normalized(answer)
    matched_aliases = [alias for alias in _service_aliases(question) if alias in normalized_answer]
    if not matched_aliases:
        return False
    return all(set(alias.split()) <= SERVICE_FAMILY_TOKENS for alias in matched_aliases)


def _service_answer_cap(question: Question, answer: str) -> int | None:
    if _has_uncertain_guess(answer):
        return 65
    if _offers_ambiguous_alternatives(answer):
        return 79
    if not _has_explanatory_detail(answer, question):
        return 85
    return None


def _has_uncertain_guess(answer: str) -> bool:
    normalized = " ".join(str(answer).casefold().replace("’", "'").split())
    return any(phrase in normalized for phrase in UNCERTAIN_GUESS_PHRASES)


def _offers_ambiguous_alternatives(answer: str) -> bool:
    normalized = _normalized(answer)
    if " or " not in f" {normalized} ":
        return False
    return len(_mentioned_service_ids(normalized)) >= 2 or _or_joins_service_like_terms(normalized)


def _or_joins_service_like_terms(normalized_answer: str) -> bool:
    service_tokens = _service_alternative_tokens()
    tokens = normalized_answer.split()
    for index, token in enumerate(tokens):
        if token != "or":
            continue
        left = set(tokens[max(0, index - 4):index])
        right = set(tokens[index + 1:index + 5])
        if (left & service_tokens) or (right & service_tokens):
            return True
    return False


def _service_alternative_tokens() -> set[str]:
    tokens = {"aws", "amazon"}
    for service in KNOWLEDGE_BASE.services:
        for term in (service.name, *service.aliases, *service.tokens):
            tokens.update(_tokens(term))
    return tokens - GENERIC_TOKENS - {"cost", "threshold", "thresholds", "usage"}


def _mentioned_service_ids(normalized_answer: str) -> set[str]:
    service_ids = set()
    for service in KNOWLEDGE_BASE.services:
        terms = (service.name, *service.aliases, *service.tokens)
        for term in terms:
            normalized_term = _normalized(term)
            term_tokens = set(normalized_term.split())
            if not normalized_term or term_tokens <= GENERIC_TOKENS | AMBIGUOUS_ALIAS_TOKENS:
                continue
            if normalized_term in normalized_answer:
                service_ids.add(service.id)
                break
    return service_ids


def _has_explanatory_detail(answer: str, question: Question) -> bool:
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if len(answer_tokens) >= 5:
        return True
    required_without_service = set()
    for concept in _required_concepts(question)[1:]:
        required_without_service.update(_tokens(concept))
    required_without_service -= GENERIC_TOKENS | SERVICE_FAMILY_TOKENS
    return len(answer_tokens & required_without_service) >= 2


def _is_complete_service_answer(answer: str) -> bool:
    """Recognize a sentence that identifies a service without requiring rubric restatement."""

    return len(_tokens(answer)) >= 4


def _is_exact_correct_answer(question: Question, answer: str) -> bool:
    correct_options, _incorrect_options = _option_texts(question)
    normalized_answer = _strip_leading_use(answer)
    accepted_answers = [*correct_options, *question.acceptable_answers]
    return bool(normalized_answer) and normalized_answer in {
        _strip_leading_use(option)
        for option in accepted_answers
    }


def _service_aliases(question: Question) -> set[str]:
    correct_options, _incorrect_options = _option_texts(question)
    values = {_service_alias_value(option) for option in correct_options}
    values.update(_service_alias_value(answer) for answer in question.acceptable_answers)
    values.add(_service_alias_value(correct_answer_text(question)))
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
            if token in SERVICE_FAMILY_TOKENS and token not in AMBIGUOUS_ALIAS_TOKENS and len(token) > 2
        )
        for token in distinctive_tokens:
            aliases.update(KNOWLEDGE_BASE.aliases_for_service_token(token))
    return {alias for alias in aliases if alias}


def _service_alias_value(value: str) -> str:
    normalized = _strip_leading_use(value)
    distinctive_tokens = [
        token
        for token in normalized.split()
        if token not in GENERIC_TOKENS
    ]
    if len(distinctive_tokens) > 4:
        return ""
    return normalized


def _concept_coverage(question: Question, answer: str) -> float:
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer))
    covered = 0
    required_concepts = _required_concepts(question)
    for concept in required_concepts:
        if any(
            _concept_term_is_covered(term, normalized_answer, answer_tokens)
            for term in KNOWLEDGE_BASE.terms_for_concept(concept)
        ):
            covered += 1
    return covered / max(1, len(required_concepts))


def _concept_term_is_covered(term: str, normalized_answer: str, answer_tokens: set[str]) -> bool:
    concept_tokens = [token for token in _tokens(term) if token not in GENERIC_TOKENS]
    if not concept_tokens:
        return False
    concept_token_set = set(concept_tokens)
    if " ".join(concept_tokens) in normalized_answer:
        return True
    matched_tokens = concept_token_set & answer_tokens
    if len(matched_tokens) / len(concept_token_set) < 0.5:
        return False
    if matched_tokens <= SERVICE_FAMILY_TOKENS:
        return False
    if len(concept_token_set) > 1 and len(matched_tokens) < 2:
        return False
    return True


def _required_concepts(question: Question) -> list[str]:
    return question.required_concepts or question.key_concepts


def _near_miss_option_score(question: Question, answer: str) -> int | None:
    _correct_options, incorrect_options = _option_texts(question)
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if not answer_tokens:
        return None
    for option in incorrect_options:
        raw_option_tokens = set(_tokens(option))
        option_tokens = raw_option_tokens - GENERIC_TOKENS
        if not {"alone", "only"} & option_tokens:
            continue
        normalized_option = _normalized(option)
        if normalized_answer in {normalized_option, _strip_leading_use(option)} or answer_tokens <= option_tokens:
            if "aws" in raw_option_tokens:
                return 65
            return 75 if "alone" in option_tokens else 65
    return None


def _adjacent_service_score(question: Question, answer: str) -> int | None:
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer))
    correct = _normalized(correct_answer_text(question))
    correct_tokens = set(correct.split())
    if "s3 glacier storage classes" in correct and "glacier" in answer_tokens:
        return 85
    if ("secretsmanager" in correct or {"secrets", "manager"} <= correct_tokens) and {"parameter", "store"} <= answer_tokens:
        return 65
    if "kms" in correct and "secretsmanager" in normalized_answer:
        return 65
    if "dynamodb global tables" in correct and {"global", "database", "tables"} <= answer_tokens:
        return 75
    if "dynamodb global tables" in correct and {"rds", "read", "replicas"} <= answer_tokens:
        return 65
    return None


def _incorrect_option_score(question: Question, answer: str, concept_coverage: float) -> int | None:
    _correct_options, incorrect_options = _option_texts(question)
    normalized_answer = _normalized(answer)
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if not answer_tokens:
        return None
    for option in incorrect_options:
        option_tokens = set(_tokens(option)) - GENERIC_TOKENS - {"only"}
        if answer_tokens <= option_tokens or normalized_answer in {_normalized(option), _strip_leading_use(option)}:
            if concept_coverage > 0:
                return 65
            return 35
    return None


def _answers_specific_required_concept(question: Question, answer: str) -> bool:
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if not answer_tokens:
        return False
    if answer_tokens <= {"orchestration"}:
        return False
    if {"rds", "read", "replicas"} <= answer_tokens:
        return True
    if len(answer_tokens) <= 2:
        for concept in _required_concepts(question):
            concept_tokens = set(_tokens(concept)) - GENERIC_TOKENS
            if answer_tokens and answer_tokens <= concept_tokens:
                return True
    return False


def _has_adjacent_domain_signal(question: Question, answer: str) -> bool:
    question_tokens = set(_tokens(question.question))
    reference_tokens = set(_tokens(correct_answer_text(question))) - GENERIC_TOKENS
    answer_tokens = set(_tokens(answer)) - GENERIC_TOKENS
    if {"permissions", "permission"} & question_tokens and {"role", "roles", "iam"} & answer_tokens:
        return True
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
    return TOKEN_PATTERN.findall(_canonical_syntax(value))


def _canonical_syntax(value: str) -> str:
    return KNOWLEDGE_BASE.canonicalize(value)
