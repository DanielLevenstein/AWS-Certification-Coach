"""JSON-backed question repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question, QuestionFilter


class JsonQuestionRepository:
    """Loads and filters certification questions from a JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._questions: list[Question] | None = None

    def all(self) -> list[Question]:
        if self._questions is None:
            self._questions = self._load_questions()
        return list(self._questions)

    def filter_questions(self, filters: QuestionFilter) -> list[Question]:
        questions = self.all()
        if filters.certification:
            questions = [q for q in questions if q.certification == filters.certification]
        if filters.domain:
            questions = [q for q in questions if q.domain == filters.domain]
        if filters.difficulty:
            questions = [q for q in questions if q.difficulty == filters.difficulty]
        return questions

    def available_certifications(self) -> list[str]:
        return _unique_sorted(q.certification for q in self.all())

    def available_domains(self) -> list[str]:
        return _unique_sorted(q.domain for q in self.all())

    def available_difficulties(self) -> list[str]:
        return _unique_sorted(q.difficulty for q in self.all())

    def _load_questions(self) -> list[Question]:
        with self.path.open("r", encoding="utf-8") as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            raise ValueError(f"Question file must contain a list: {self.path}")
        return [question_from_json(row) for row in rows]


def question_from_json(row: object) -> Question:
    if not isinstance(row, dict):
        raise ValueError("Question rows must be JSON objects.")
    required = [
        "certification",
        "domain",
        "difficulty",
        "question",
        "reference_answer",
        "key_concepts",
    ]
    missing = [field for field in required if field not in row]
    if missing:
        raise ValueError(f"Question is missing required fields: {', '.join(missing)}")
    key_concepts = row["key_concepts"]
    if not isinstance(key_concepts, list):
        raise ValueError("Question key_concepts must be a list.")
    return Question(
        certification=str(row["certification"]),
        domain=str(row["domain"]),
        difficulty=str(row["difficulty"]),
        question=str(row["question"]),
        reference_answer=str(row["reference_answer"]),
        key_concepts=[str(concept) for concept in key_concepts],
        original_multiple_choice=_multiple_choice_from_json(row.get("original_multiple_choice")),
    )


def _unique_sorted(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def _multiple_choice_from_json(value: object) -> MultipleChoiceQuestion | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("original_multiple_choice must be a JSON object.")
    options = value.get("options", [])
    if not isinstance(options, list):
        raise ValueError("original_multiple_choice.options must be a list.")
    return MultipleChoiceQuestion(
        question=str(value.get("question", "")),
        options=[
            MultipleChoiceOption(
                option_id=str(option.get("option_id", "")),
                text=str(option.get("text", "")),
            )
            for option in options
            if isinstance(option, dict)
        ],
        correct_option_ids=[str(option_id) for option_id in value.get("correct_option_ids", [])],
        explanation=str(value.get("explanation", "")),
        source_name=str(value.get("source_name", "")),
        source_url=str(value.get("source_url", "")),
        source_license_notes=str(value.get("source_license_notes", "")),
    )
