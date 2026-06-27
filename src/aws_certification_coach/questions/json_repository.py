"""JSON-backed question repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question, QuestionFilter
from aws_certification_coach.mongodb import get_mongodb_database, mongodb_content_enabled, mongodb_database_name, mongodb_uri

DEFAULT_GENERATED_QUESTIONS_PATH = Path(__file__).resolve().parents[3] / "data" / "questions" / "sample_questions.json"


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
        if self.path.resolve() == DEFAULT_GENERATED_QUESTIONS_PATH.resolve() and mongodb_content_enabled():
            database = get_mongodb_database(mongodb_uri(), mongodb_database_name())
            rows = list(database["generated_questions"].find({}, {"_id": False}))
            if rows:
                return [question_from_json(row) for row in rows]
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
        schema_version=int(row.get("schema_version", 1)),
        certification=str(row["certification"]),
        domain=str(row["domain"]),
        difficulty=str(row["difficulty"]),
        question=str(row["question"]),
        reference_answer=str(row["reference_answer"]),
        key_concepts=[str(concept) for concept in key_concepts],
        source_url=str(row.get("source_url", "")),
        question_type=str(row.get("question_type", "service_selection")),
        required_concepts=_string_list_from_json(row.get("required_concepts", key_concepts)),
        bonus_concepts=_string_list_from_json(row.get("bonus_concepts", [])),
        common_misconceptions=_string_list_from_json(row.get("common_misconceptions", [])),
        acceptable_answers=_string_list_from_json(row.get("acceptable_answers", [])),
        must_not_claim=_string_list_from_json(row.get("must_not_claim", [])),
        do_not_claim_explanation=_string_list_from_json(row.get("do_not_claim_explanation", [])),
        exam_code=str(row.get("exam_code", "")),
        original_multiple_choice=_multiple_choice_from_json(row.get("original_multiple_choice")),
        artifact_type=str(row.get("artifact_type", "")),
        artifact_language=str(row.get("artifact_language", "")),
        artifact_body=str(row.get("artifact_body", "")),
        artifact_context=str(row.get("artifact_context", "")),
        expected_issue=str(row.get("expected_issue", "")),
    )


def _unique_sorted(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def _string_list_from_json(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _string_dict_from_json(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


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
                source_url=str(option.get("source_url", "")),
                metadata=_string_dict_from_json(option.get("metadata", {})),
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
