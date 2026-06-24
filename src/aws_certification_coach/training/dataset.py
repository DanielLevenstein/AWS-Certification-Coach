"""Dataset loading for answer classification training."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.questions.json_repository import question_from_json
from aws_certification_coach.ratings import letter_to_binary_label, letter_to_numeric


@dataclass(frozen=True)
class AnswerClassificationExample:
    question: Question
    answer: str
    label: int
    source: str = ""


@dataclass(frozen=True)
class GradedAnswerExample:
    question: Question
    answer: str
    rating: float
    source: str = ""


def load_answer_classification_examples(path: str | Path) -> list[AnswerClassificationExample]:
    rows = _load_rows(path)
    examples: list[AnswerClassificationExample] = []
    for row in rows:
        examples.extend(_classification_examples_from_json(row))
    return examples


def load_feedback_classification_examples(
    path: str | Path,
    questions: list[Question],
    max_schema_version: str | float | int | None = None,
) -> list[AnswerClassificationExample]:
    return [
        AnswerClassificationExample(
            question=_feedback_question(row, questions),
            answer=str(row["answer_given"]),
            label=letter_to_binary_label(row["correct_rating"]),
            source="user_feedback",
        )
        for row in _feedback_rows(path, max_schema_version)
        if isinstance(row, dict)
    ]


def load_feedback_graded_examples(
    path: str | Path,
    questions: list[Question],
    max_schema_version: str | float | int | None = None,
) -> list[GradedAnswerExample]:
    return [
        GradedAnswerExample(
            question=_feedback_question(row, questions),
            answer=str(row["answer_given"]),
            rating=letter_to_numeric(row["correct_rating"]),
            source="user_feedback",
        )
        for row in _feedback_rows(path, max_schema_version)
        if isinstance(row, dict)
    ]


def _load_rows(path: str | Path) -> list[object]:
    with Path(path).open("r", encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"Training data must be a JSON list: {path}")
    return rows


def _feedback_rows(path: str | Path, max_schema_version: str | float | int | None) -> list[object]:
    rows = _load_rows(path)
    if max_schema_version is None:
        return rows
    maximum = _schema_decimal(max_schema_version)
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        schema_version = row.get("schema_version", 1)
        if _schema_decimal(schema_version) > maximum:
            raise ValueError(
                f"Feedback row {index} in {path} uses schema_version {schema_version}, "
                f"which is newer than supported schema {max_schema_version}."
            )
    return rows


def _schema_decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid feedback schema_version: {value!r}") from exc


def _classification_examples_from_json(row: object) -> list[AnswerClassificationExample]:
    if not isinstance(row, dict):
        raise ValueError("Training examples must be JSON objects.")
    question = question_from_json(row)
    if "binary_answers" in row:
        answers = row["binary_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question binary_answers must be a list.")
        examples = [
            AnswerClassificationExample(
                question=question,
                answer=str(answer["answer"]),
                label=int(answer["label"]),
                source=str(answer.get("source", "")),
            )
            for answer in answers
            if isinstance(answer, dict)
        ]
        partial_answers = row.get("partial_answers", [])
        if isinstance(partial_answers, list):
            examples.extend(
                AnswerClassificationExample(
                    question=question,
                    answer=str(answer["answer"]),
                    label=0,
                    source=str(answer.get("source", "partial_rejected")),
                )
                for answer in partial_answers
                if isinstance(answer, dict) and _is_rejected_partial_answer(answer)
            )
        return examples
    if "generated_answers" in row:
        answers = row["generated_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question generated_answers must be a list.")
        return [
            AnswerClassificationExample(
                question=question,
                answer=str(answer["answer"]),
                label=letter_to_binary_label(answer["rating"]),
                source=str(answer.get("source", "generated_answer")),
            )
            for answer in answers
            if isinstance(answer, dict)
        ]
    return [
        AnswerClassificationExample(
            question=question,
            answer=str(row["answer"]),
            label=int(row["label"]),
            source=str(row.get("source", "")),
        )
    ]


def _is_rejected_partial_answer(answer: dict) -> bool:
    try:
        return float(answer.get("rating_bucket", answer.get("rating", 1.0))) <= 0.25
    except (TypeError, ValueError):
        return False


def question_signature(question: Question) -> tuple[str, str, str]:
    original = question.original_multiple_choice
    return (
        _normalized_joined(question.question),
        _normalized_joined(question.reference_answer),
        _normalized_joined(original.question if original else ""),
    )


def _feedback_question(row: dict, questions: list[Question]) -> Question:
    question_text = _normalized_text(row.get("question", ""))
    reference_text = _normalized_text(row.get("reference_answer", ""))
    original_question_text = _normalized_text(_feedback_original_question(row))
    ranked = sorted(
        (
            (
                _feedback_match_score(
                    question_text,
                    reference_text,
                    original_question_text,
                    question,
                ),
                question_signature(question),
                question,
            )
            for question in questions
        ),
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )
    if not ranked or ranked[0][0] <= 0:
        raise ValueError(f"Could not match feedback to a known question: {row.get('question', '')!r}")
    return ranked[0][2]


def _feedback_match_score(
    question_text: set[str],
    reference_text: set[str],
    original_question_text: set[str],
    question: Question,
) -> float:
    original = question.original_multiple_choice
    return _jaccard(question_text, _normalized_text(question.question)) + _jaccard(
        reference_text,
        _normalized_text(question.reference_answer),
    ) + _jaccard(
        original_question_text,
        _normalized_text(original.question if original else ""),
    )


def _feedback_original_question(row: dict) -> object:
    original = row.get("original_multiple_choice")
    if not isinstance(original, dict):
        return ""
    return original.get("question", "")


def _normalized_text(value: object) -> set[str]:
    return {token.strip(".,:;!?()[]").casefold() for token in str(value).split() if token.strip(".,:;!?()[]")}


def _normalized_joined(value: object) -> str:
    return " ".join(sorted(_normalized_text(value)))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
