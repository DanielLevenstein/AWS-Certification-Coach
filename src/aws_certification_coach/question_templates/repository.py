"""Validated, cached access to question-generation templates."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path


DEFAULT_QUESTION_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "question_templates"
    / "question_template.json"
)
KNOWN_TEMPLATE_SLOTS = {
    "concepts",
    "distractors",
    "purpose",
    "service_id",
    "service_name",
}
FORBIDDEN_TEMPLATE_KEYS = {
    "answer",
    "correct_rating",
    "grade",
    "partial_answers",
    "rating",
}


@dataclass(frozen=True)
class QuestionTemplate:
    id: str
    question_type: str
    certifications: tuple[str, ...]
    prompt_variants: tuple[str, ...]
    question_pattern: str
    reference_answer_pattern: str
    option_pattern: str
    required_slots: tuple[str, ...]
    rubric_merge: dict[str, str]


@dataclass(frozen=True)
class QuestionTemplateCatalog:
    schema_version: int
    description: str
    templates: tuple[QuestionTemplate, ...]

    def get(self, template_id: str) -> QuestionTemplate:
        for template in self.templates:
            if template.id == template_id:
                return template
        raise KeyError(f"Unknown question template: {template_id}")


def load_question_templates(path: str | Path = DEFAULT_QUESTION_TEMPLATE_PATH) -> QuestionTemplateCatalog:
    """Load question templates once per resolved path."""

    return _load_question_templates(str(Path(path).resolve()))


@lru_cache(maxsize=8)
def _load_question_templates(resolved_path: str) -> QuestionTemplateCatalog:
    source = Path(resolved_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    _validate_payload(payload, source)
    return QuestionTemplateCatalog(
        schema_version=int(payload["schema_version"]),
        description=str(payload["description"]),
        templates=tuple(
            QuestionTemplate(
                id=str(row["id"]),
                question_type=str(row["question_type"]),
                certifications=tuple(str(value) for value in row["certifications"]),
                prompt_variants=tuple(str(value) for value in row["prompt_variants"]),
                question_pattern=str(row["question_pattern"]),
                reference_answer_pattern=str(row["reference_answer_pattern"]),
                option_pattern=str(row["option_pattern"]),
                required_slots=tuple(str(value) for value in row["required_slots"]),
                rubric_merge={str(key): str(value) for key, value in row["rubric_merge"].items()},
            )
            for row in payload["templates"]
        ),
    )


def _validate_payload(payload: object, source: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"Question templates must be a JSON object: {source}")
    required = {"schema_version", "description", "templates"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Question templates are missing fields {sorted(missing)}: {source}")
    if payload["schema_version"] != 1:
        raise ValueError(f"Unsupported question-template schema version: {payload['schema_version']}")
    forbidden = _find_forbidden_keys(payload)
    if forbidden:
        raise ValueError(f"Question templates contain answer-label fields {sorted(forbidden)}: {source}")
    templates = payload["templates"]
    if not isinstance(templates, list) or not templates:
        raise ValueError(f"Question-template section 'templates' must be a non-empty list: {source}")
    template_ids: list[str] = []
    for index, row in enumerate(templates):
        _validate_template_row(row, index, source)
        template_ids.append(str(row["id"]))
    if len(template_ids) != len(set(template_ids)):
        raise ValueError(f"Duplicate question-template IDs in {source}")


def _validate_template_row(row: object, index: int, source: Path) -> None:
    required = {
        "id",
        "question_type",
        "certifications",
        "prompt_variants",
        "question_pattern",
        "reference_answer_pattern",
        "option_pattern",
        "required_slots",
        "rubric_merge",
    }
    if not isinstance(row, dict) or required - row.keys():
        raise ValueError(f"Invalid question-template row {index}: {source}")
    for list_field in ("certifications", "prompt_variants", "required_slots"):
        value = row[list_field]
        if not isinstance(value, list) or not all(str(item).strip() for item in value):
            raise ValueError(f"Question-template row {index} has invalid {list_field}: {source}")
    if not isinstance(row["rubric_merge"], dict) or not row["rubric_merge"]:
        raise ValueError(f"Question-template row {index} has invalid rubric_merge: {source}")
    unknown_slots = set(str(slot) for slot in row["required_slots"]) - KNOWN_TEMPLATE_SLOTS
    if unknown_slots:
        raise ValueError(f"Question-template row {index} has unknown slots {sorted(unknown_slots)}: {source}")


def _find_forbidden_keys(value: object) -> set[str]:
    found = set()
    if isinstance(value, dict):
        found.update(FORBIDDEN_TEMPLATE_KEYS & value.keys())
        for nested in value.values():
            found.update(_find_forbidden_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(_find_forbidden_keys(nested))
    return found
