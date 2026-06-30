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
KNOWN_QUESTION_CATEGORIES = {
    "cost_tradeoff",
    "operational_complexity_tradeoff",
    "latency_tradeoff",
    "durability_availability_tradeoff",
    "managed_vs_self_managed_tradeoff",
    "event_driven_vs_batch_tradeoff",
    "security_boundary_tradeoff",
    "resilience_recovery",
    "scaling_performance",
    "networking_delivery",
    "security_identity",
    "observability_governance",
    "integration_workflows",
    "data_analytics",
    "storage_data_management",
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
    option_order: tuple[str, ...]
    selection_rule: dict[str, object]
    distractor_recipes: tuple[dict[str, str], ...]
    required_slots: tuple[str, ...]
    rubric_merge: dict[str, str]
    composition_rules: dict[str, str]


@dataclass(frozen=True)
class ServiceScenario:
    id: str
    service_id: str
    domain: str
    certification: str
    exam_code: str
    difficulty: str
    purpose: str
    key_concepts: tuple[str, ...]
    distractors: tuple[str, ...]
    question_category: str


@dataclass(frozen=True)
class DeveloperQuestionScenario:
    id: str
    generated_question: str
    correct_option: str
    reference_answer: str
    distractors: tuple[str, ...]
    acceptable_answer_aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class QuestionTemplateCatalog:
    schema_version: int
    description: str
    templates: tuple[QuestionTemplate, ...]
    service_scenarios: tuple[ServiceScenario, ...]
    developer_question_scenarios: tuple[DeveloperQuestionScenario, ...]

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
                option_order=tuple(str(value) for value in row["option_order"]),
                selection_rule=dict(row["selection_rule"]),
                distractor_recipes=tuple(
                    {str(key): str(value) for key, value in recipe.items()}
                    for recipe in row["distractor_recipes"]
                ),
                required_slots=tuple(str(value) for value in row["required_slots"]),
                rubric_merge={str(key): str(value) for key, value in row["rubric_merge"].items()},
                composition_rules={str(key): str(value) for key, value in row["composition_rules"].items()},
            )
            for row in payload["templates"]
        ),
        service_scenarios=tuple(
            ServiceScenario(
                id=str(row["id"]),
                service_id=str(row["service_id"]),
                domain=str(row["domain"]),
                certification=str(row["certification"]),
                exam_code=str(row["exam_code"]),
                difficulty=str(row["difficulty"]),
                purpose=str(row["purpose"]),
                key_concepts=tuple(str(value) for value in row["key_concepts"]),
                distractors=tuple(str(value) for value in row["distractors"]),
                question_category=str(row["question_category"]),
            )
            for row in payload["service_scenarios"]
        ),
        developer_question_scenarios=tuple(
            DeveloperQuestionScenario(
                id=str(row["id"]),
                generated_question=str(row["generated_question"]),
                correct_option=str(row["correct_option"]),
                reference_answer=str(row["reference_answer"]),
                distractors=tuple(str(value) for value in row["distractors"]),
                acceptable_answer_aliases=tuple(str(value) for value in row.get("acceptable_answer_aliases", [])),
            )
            for row in payload["developer_question_scenarios"]
        ),
    )


def _validate_payload(payload: object, source: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"Question templates must be a JSON object: {source}")
    required = {"schema_version", "description", "templates", "service_scenarios", "developer_question_scenarios"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Question templates are missing fields {sorted(missing)}: {source}")
    if payload["schema_version"] < 2:
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
    scenarios = payload["service_scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError(f"Question-template section 'service_scenarios' must be a non-empty list: {source}")
    scenario_ids: list[str] = []
    for index, row in enumerate(scenarios):
        _validate_service_scenario_row(row, index, source)
        scenario_ids.append(str(row["id"]))
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError(f"Duplicate service-scenario IDs in {source}")
    developer_scenarios = payload["developer_question_scenarios"]
    if not isinstance(developer_scenarios, list) or not developer_scenarios:
        raise ValueError(f"Question-template section 'developer_question_scenarios' must be a non-empty list: {source}")
    developer_scenario_ids: list[str] = []
    for index, row in enumerate(developer_scenarios):
        _validate_developer_question_scenario_row(row, index, source)
        developer_scenario_ids.append(str(row["id"]))
    if len(developer_scenario_ids) != len(set(developer_scenario_ids)):
        raise ValueError(f"Duplicate developer-question scenario IDs in {source}")


def _validate_template_row(row: object, index: int, source: Path) -> None:
    required = {
        "id",
        "question_type",
        "certifications",
        "prompt_variants",
        "question_pattern",
        "reference_answer_pattern",
        "option_pattern",
        "option_order",
        "selection_rule",
        "distractor_recipes",
        "required_slots",
        "rubric_merge",
        "composition_rules",
    }
    if not isinstance(row, dict) or required - row.keys():
        raise ValueError(f"Invalid question-template row {index}: {source}")
    for list_field in ("certifications", "prompt_variants", "option_order", "distractor_recipes", "required_slots"):
        value = row[list_field]
        if not isinstance(value, list) or not all(str(item).strip() for item in value):
            raise ValueError(f"Question-template row {index} has invalid {list_field}: {source}")
    for dict_field in ("selection_rule", "rubric_merge", "composition_rules"):
        if not isinstance(row[dict_field], dict) or not row[dict_field]:
            raise ValueError(f"Question-template row {index} has invalid {dict_field}: {source}")
    if row["option_order"].count("correct") != 1 or len(row["option_order"]) < 2:
        raise ValueError(f"Question-template row {index} has invalid option_order: {source}")
    unknown_slots = set(str(slot) for slot in row["required_slots"]) - KNOWN_TEMPLATE_SLOTS
    if unknown_slots:
        raise ValueError(f"Question-template row {index} has unknown slots {sorted(unknown_slots)}: {source}")


def _validate_service_scenario_row(row: object, index: int, source: Path) -> None:
    required = {
        "id",
        "service_id",
        "domain",
        "certification",
        "exam_code",
        "difficulty",
        "purpose",
        "key_concepts",
        "distractors",
        "question_category",
    }
    if not isinstance(row, dict) or required - row.keys():
        raise ValueError(f"Invalid service-scenario row {index}: {source}")
    for text_field in ("id", "service_id", "domain", "certification", "exam_code", "difficulty", "purpose"):
        if not str(row[text_field]).strip():
            raise ValueError(f"Service-scenario row {index} has invalid {text_field}: {source}")
    for list_field in ("key_concepts", "distractors"):
        value = row[list_field]
        if not isinstance(value, list) or not all(str(item).strip() for item in value):
            raise ValueError(f"Service-scenario row {index} has invalid {list_field}: {source}")
    if len(row["distractors"]) < 3:
        raise ValueError(f"Service-scenario row {index} needs at least three distractors: {source}")
    question_category = str(row["question_category"])
    if question_category not in KNOWN_QUESTION_CATEGORIES:
        raise ValueError(
            f"Service-scenario row {index} has unknown question_category {question_category!r}: {source}"
        )


def _validate_developer_question_scenario_row(row: object, index: int, source: Path) -> None:
    required = {
        "id",
        "generated_question",
        "correct_option",
        "reference_answer",
        "distractors",
    }
    if not isinstance(row, dict) or required - row.keys():
        raise ValueError(f"Invalid developer-question scenario row {index}: {source}")
    for text_field in ("id", "generated_question", "correct_option", "reference_answer"):
        if not str(row[text_field]).strip():
            raise ValueError(f"Developer-question scenario row {index} has invalid {text_field}: {source}")
    value = row["distractors"]
    if not isinstance(value, list) or not all(str(item).strip() for item in value):
        raise ValueError(f"Developer-question scenario row {index} has invalid distractors: {source}")
    if len(value) < 3:
        raise ValueError(f"Developer-question scenario row {index} needs at least three distractors: {source}")
    aliases = row.get("acceptable_answer_aliases", [])
    if not isinstance(aliases, list) or not all(str(item).strip() for item in aliases):
        raise ValueError(f"Developer-question scenario row {index} has invalid acceptable_answer_aliases: {source}")


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
