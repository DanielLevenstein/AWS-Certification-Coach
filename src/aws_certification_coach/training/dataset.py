"""Dataset loading for answer classification training."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.ratings import letter_to_binary_label, letter_to_numeric


@dataclass(frozen=True)
class AnswerClassificationExample:
    question_id: str
    answer: str
    label: int
    source: str = ""


@dataclass(frozen=True)
class AnswerRegressionExample:
    question_id: str
    answer: str
    rating: float
    source: str = ""


def load_answer_classification_examples(path: str | Path) -> list[AnswerClassificationExample]:
    rows = _load_rows(path)
    examples: list[AnswerClassificationExample] = []
    for row in rows:
        examples.extend(_classification_examples_from_json(row))
    return examples


def load_answer_regression_examples(path: str | Path) -> list[AnswerRegressionExample]:
    rows = _load_rows(path)
    examples: list[AnswerRegressionExample] = []
    for row in rows:
        examples.extend(_regression_examples_from_json(row))
    return examples


def load_feedback_classification_examples(
    path: str | Path,
    questions_by_id: dict[str, Question],
) -> list[AnswerClassificationExample]:
    return [
        AnswerClassificationExample(
            question_id=_feedback_question_id(row, questions_by_id),
            answer=str(row["answer_given"]),
            label=letter_to_binary_label(row["correct_rating"]),
            source="user_feedback",
        )
        for row in _load_rows(path)
        if isinstance(row, dict)
    ]


def load_feedback_regression_examples(
    path: str | Path,
    questions_by_id: dict[str, Question],
) -> list[AnswerRegressionExample]:
    return [
        AnswerRegressionExample(
            question_id=_feedback_question_id(row, questions_by_id),
            answer=str(row["answer_given"]),
            rating=letter_to_numeric(row["correct_rating"]),
            source="user_feedback",
        )
        for row in _load_rows(path)
        if isinstance(row, dict)
    ]


def _load_rows(path: str | Path) -> list[object]:
    with Path(path).open("r", encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"Training data must be a JSON list: {path}")
    return rows


def _classification_examples_from_json(row: object) -> list[AnswerClassificationExample]:
    if not isinstance(row, dict):
        raise ValueError("Training examples must be JSON objects.")
    if "binary_answers" in row:
        question_id = str(row["question_id"])
        answers = row["binary_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question binary_answers must be a list.")
        examples = [
            AnswerClassificationExample(
                question_id=str(answer.get("question_id", question_id)),
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
                    question_id=str(answer.get("question_id", question_id)),
                    answer=str(answer["answer"]),
                    label=0,
                    source=str(answer.get("source", "partial_rejected")),
                )
                for answer in partial_answers
                if isinstance(answer, dict) and _is_rejected_partial_answer(answer)
            )
        return examples
    if "generated_answers" in row:
        question_id = str(row["question_id"])
        answers = row["generated_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question generated_answers must be a list.")
        return [
            AnswerClassificationExample(
                question_id=str(answer.get("question_id", question_id)),
                answer=str(answer["answer"]),
                label=letter_to_binary_label(answer["rating"]),
                source=str(answer.get("source", "generated_answer")),
            )
            for answer in answers
            if isinstance(answer, dict)
        ]
    return [
        AnswerClassificationExample(
            question_id=str(row["question_id"]),
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


def _regression_examples_from_json(row: object) -> list[AnswerRegressionExample]:
    if not isinstance(row, dict):
        raise ValueError("Training examples must be JSON objects.")
    if "partial_answers" in row:
        question_id = str(row["question_id"])
        answers = row["partial_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question partial_answers must be a list.")
        return [
            AnswerRegressionExample(
                question_id=str(answer.get("question_id", question_id)),
                answer=str(answer["answer"]),
                rating=float(answer["rating"]),
                source=str(answer.get("source", "")),
            )
            for answer in answers
            if isinstance(answer, dict)
        ]
    if "generated_answers" in row:
        question_id = str(row["question_id"])
        answers = row["generated_answers"]
        if not isinstance(answers, list):
            raise ValueError("Combined question generated_answers must be a list.")
        return [
            AnswerRegressionExample(
                question_id=str(answer.get("question_id", question_id)),
                answer=str(answer["answer"]),
                rating=letter_to_numeric(answer["rating"]),
                source=str(answer.get("source", "generated_answer")),
            )
            for answer in answers
            if isinstance(answer, dict)
        ]
    if "rating" not in row:
        return []
    return [
        AnswerRegressionExample(
            question_id=str(row["question_id"]),
            answer=str(row["answer"]),
            rating=float(row["rating"]),
            source=str(row.get("source", "")),
        )
    ]


def _feedback_question_id(row: dict, questions_by_id: dict[str, Question]) -> str:
    question_id = str(row.get("question_id", "")).strip()
    if question_id in questions_by_id:
        return question_id

    question_text = _normalized_text(row.get("question", ""))
    reference_text = _normalized_text(row.get("reference_answer", ""))
    ranked = sorted(
        (
            (_feedback_match_score(question_text, reference_text, question), candidate_id)
            for candidate_id, question in questions_by_id.items()
        ),
        reverse=True,
    )
    if not ranked or ranked[0][0] <= 0:
        raise ValueError(f"Could not match feedback to a known question: {row.get('question', '')!r}")
    return ranked[0][1]


def _feedback_match_score(question_text: set[str], reference_text: set[str], question: Question) -> float:
    return _jaccard(question_text, _normalized_text(question.question)) + _jaccard(
        reference_text,
        _normalized_text(question.reference_answer),
    )


def _normalized_text(value: object) -> set[str]:
    return {token.strip(".,:;!?()[]").casefold() for token in str(value).split() if token.strip(".,:;!?()[]")}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
