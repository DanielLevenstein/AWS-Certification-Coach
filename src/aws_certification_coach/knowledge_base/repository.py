"""Validated, cached access to canonical AWS knowledge."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Iterable

from aws_certification_coach.question_templates import load_question_templates
from aws_certification_coach.questions.rubric_metadata import service_selection_rubric_metadata


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
DEFAULT_KNOWLEDGE_BASE_PATH = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "knowledge_base"
    / "knowledge_base.json"
)
FORBIDDEN_CONTENT_KEYS = {
    "answer",
    "correct_rating",
    "grade",
    "partial_answers",
    "question",
    "rating",
    "reference_answer",
}


@dataclass(frozen=True)
class Service:
    id: str
    name: str
    tokens: tuple[str, ...]
    aliases: tuple[str, ...]
    source_url: str
    description: str


@dataclass(frozen=True)
class Concept:
    id: str
    name: str
    aliases: tuple[str, ...]
    service_ids: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class QuestionFlagSet:
    id: str
    key_concepts: tuple[str, ...]
    common_misconceptions: tuple[str, ...]
    acceptable_answers: tuple[str, ...]
    must_not_claim: tuple[str, ...]
    do_not_claim_explanation: tuple[str, ...]
    source_url: str


@dataclass(frozen=True)
class KnowledgeSelection:
    concepts: tuple[Concept, ...]
    services: tuple[Service, ...]

    def render(self, max_characters: int = 1600) -> str:
        """Render deterministic, bounded context suitable for a small local model."""

        blocks = []
        services_by_id = {service.id: service for service in self.services}
        for concept in self.concepts:
            service_names = [
                services_by_id[service_id].name
                for service_id in concept.service_ids
                if service_id in services_by_id
            ]
            block = "\n".join(
                (
                    f"CONCEPT: {concept.name}",
                    f"SERVICES: {', '.join(service_names)}",
                    f"MEANING: {concept.description}",
                    f"ALIASES: {', '.join(concept.aliases) if concept.aliases else 'none'}",
                )
            )
            candidate = "\n\n".join((*blocks, block))
            if len(candidate) > max_characters:
                break
            blocks.append(block)
        return "\n\n".join(blocks)


@dataclass(frozen=True)
class KnowledgeBase:
    schema_version: int
    description: str
    syntax_aliases: tuple[tuple[str, str], ...]
    services: tuple[Service, ...]
    concepts: tuple[Concept, ...]
    common_misconceptions: tuple[QuestionFlagSet, ...] = ()
    must_not_claim: tuple[QuestionFlagSet, ...] = ()

    @property
    def service_tokens(self) -> frozenset[str]:
        return frozenset(token for service in self.services for token in service.tokens)

    def canonicalize(self, value: str) -> str:
        normalized = " ".join(TOKEN_PATTERN.findall(value.casefold()))
        for alias, canonical in sorted(self.syntax_aliases, key=lambda item: len(item[0]), reverse=True):
            normalized = re.sub(rf"\b{re.escape(alias)}\b", canonical, normalized)
        return normalized

    def aliases_for_service_token(self, token: str) -> frozenset[str]:
        normalized_token = self.canonicalize(token)
        aliases = set()
        for service in self.services:
            if normalized_token not in service.tokens:
                continue
            aliases.update(self.canonicalize(alias) for alias in service.aliases)
        return frozenset(alias for alias in aliases if alias)

    def service_by_id(self, service_id: str) -> Service:
        for service in self.services:
            if service.id == service_id:
                return service
        raise KeyError(f"Unknown service ID: {service_id}")

    def service_for_name(self, name: str) -> Service | None:
        normalized = self.canonicalize(name)
        for service in self.services:
            terms = (service.name, *service.aliases, *service.tokens)
            if normalized in {self.canonicalize(term) for term in terms}:
                return service
        return None

    def terms_for_concept(self, name: str) -> tuple[str, ...]:
        normalized_name = self.canonicalize(name)
        for concept in self.concepts:
            if self.canonicalize(concept.name) == normalized_name:
                return tuple(dict.fromkeys((concept.name, *concept.aliases)))
        return (name,)

    def flag_sets_for_source_url(self, source_url: str) -> tuple[QuestionFlagSet, ...]:
        if not source_url:
            return ()
        matched: list[QuestionFlagSet] = []
        seen_ids: set[str] = set()
        for row in (*self.common_misconceptions, *self.must_not_claim):
            if row.source_url != source_url or row.id in seen_ids:
                continue
            matched.append(row)
            seen_ids.add(row.id)
        return tuple(matched)

    def select(self, concept_names: Iterable[str], answer: str = "") -> KnowledgeSelection:
        """Select exact requested concepts, then relevant alias matches from the answer."""

        requested = {self.canonicalize(name) for name in concept_names if name.strip()}
        normalized_answer = self.canonicalize(answer)
        selected = []
        for concept in self.concepts:
            terms = (concept.name, *concept.aliases)
            normalized_terms = {self.canonicalize(term) for term in terms}
            requested_match = self.canonicalize(concept.name) in requested
            answer_match = any(
                re.search(rf"\b{re.escape(term)}\b", normalized_answer)
                for term in normalized_terms
                if term
            )
            if requested_match or answer_match:
                selected.append(concept)
        service_ids = {service_id for concept in selected for service_id in concept.service_ids}
        services = tuple(service for service in self.services if service.id in service_ids)
        return KnowledgeSelection(tuple(selected), services)


def load_knowledge_base(path: str | Path = DEFAULT_KNOWLEDGE_BASE_PATH) -> KnowledgeBase:
    """Load a knowledge document once per resolved path."""

    return _load_knowledge_base(str(Path(path).resolve()))


@lru_cache(maxsize=8)
def _load_knowledge_base(resolved_path: str) -> KnowledgeBase:
    source = Path(resolved_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    _validate_payload(payload, source)
    services = tuple(
        Service(
            id=str(row["id"]),
            name=str(row["name"]),
            tokens=tuple(str(value) for value in row["tokens"]),
            aliases=tuple(str(value) for value in row["aliases"]),
            source_url=str(row["source_url"]),
            description=str(row["description"]),
        )
        for row in payload["services"]
    )
    concepts = tuple(
        Concept(
            id=str(row["id"]),
            name=str(row["name"]),
            aliases=tuple(str(value) for value in row["aliases"]),
            service_ids=tuple(str(value) for value in row["service_ids"]),
            description=str(row["description"]),
        )
        for row in payload["concepts"]
    )
    common_misconceptions = _load_flag_sets(payload, services)
    must_not_claim = tuple(
        _flag_set_from_json(row)
        for row in payload.get("must_not_claim", [])
    ) or common_misconceptions
    knowledge = KnowledgeBase(
        schema_version=int(payload["schema_version"]),
        description=str(payload["description"]),
        syntax_aliases=tuple(
            (str(row["alias"]), str(row["canonical"]))
            for row in payload["syntax_aliases"]
        ),
        services=services,
        concepts=concepts,
        common_misconceptions=common_misconceptions,
        must_not_claim=must_not_claim,
    )
    _validate_normalized_values(knowledge, source)
    return knowledge


def _validate_payload(payload: object, source: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"Knowledge base must be a JSON object: {source}")
    required = {
        "schema_version",
        "description",
        "syntax_aliases",
        "services",
        "concepts",
    }
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Knowledge base is missing fields {sorted(missing)}: {source}")
    if payload["schema_version"] < 2:
        raise ValueError(f"Unsupported knowledge base schema version: {payload['schema_version']}")
    forbidden = _find_forbidden_keys(payload)
    if forbidden:
        raise ValueError(f"Knowledge base contains answer-label fields {sorted(forbidden)}: {source}")
    _require_rows(payload["syntax_aliases"], {"alias", "canonical"}, "syntax_aliases", source)
    _require_rows(
        payload["services"],
        {"id", "name", "tokens", "aliases", "source_url", "description"},
        "services",
        source,
    )
    _require_rows(
        payload["concepts"],
        {"id", "name", "aliases", "service_ids", "description"},
        "concepts",
        source,
    )
    _validate_flag_rows(payload, source)


def _validate_flag_rows(payload: dict[str, object], source: Path) -> None:
    flag_fields = {
        "id",
        "key_concepts",
        "common_misconceptions",
        "acceptable_answers",
        "must_not_claim",
        "do_not_claim_explanation",
        "source_url",
    }
    if "common_misconceptions" in payload:
        _require_rows(payload["common_misconceptions"], flag_fields, "common_misconceptions", source)
    if "must_not_claim" in payload:
        _require_rows(payload["must_not_claim"], flag_fields, "must_not_claim", source)


def _load_flag_sets(payload: dict[str, object], services: tuple[Service, ...]) -> tuple[QuestionFlagSet, ...]:
    if "common_misconceptions" in payload:
        return tuple(_flag_set_from_json(row) for row in payload["common_misconceptions"])
    return _generated_question_flag_sets(services)


def _generated_question_flag_sets(services: tuple[Service, ...]) -> tuple[QuestionFlagSet, ...]:
    services_by_id = {service.id: service for service in services}
    rows: list[QuestionFlagSet] = []
    for scenario in load_question_templates().service_scenarios:
        service = services_by_id.get(scenario.service_id)
        if service is None:
            continue
        correct_option = f"Use {service.name}."
        reference_answer = f"Use {service.name} to {scenario.purpose}."
        metadata = service_selection_rubric_metadata(
            service.name,
            scenario.key_concepts,
            scenario.distractors,
            correct_option,
            reference_answer,
            scenario.purpose,
        )
        rows.append(
            QuestionFlagSet(
                id=scenario.id,
                key_concepts=scenario.key_concepts,
                common_misconceptions=tuple(metadata["common_misconceptions"]),
                acceptable_answers=tuple(metadata["acceptable_answers"]),
                must_not_claim=tuple(metadata["must_not_claim"]),
                do_not_claim_explanation=tuple(metadata["do_not_claim_explanation"]),
                source_url=service.source_url,
            )
        )
    return tuple(rows)


def _flag_set_from_json(row: dict[str, object]) -> QuestionFlagSet:
    return QuestionFlagSet(
        id=str(row["id"]),
        key_concepts=tuple(str(value) for value in row["key_concepts"]),
        common_misconceptions=tuple(str(value) for value in row["common_misconceptions"]),
        acceptable_answers=tuple(str(value) for value in row["acceptable_answers"]),
        must_not_claim=tuple(str(value) for value in row["must_not_claim"]),
        do_not_claim_explanation=tuple(str(value) for value in row["do_not_claim_explanation"]),
        source_url=str(row["source_url"]),
    )


def _require_rows(value: object, required: set[str], section: str, source: Path) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"Knowledge base section {section!r} must be a non-empty list: {source}")
    for index, row in enumerate(value):
        if not isinstance(row, dict) or required - row.keys():
            raise ValueError(f"Invalid {section} row {index}: {source}")


def _find_forbidden_keys(value: object) -> set[str]:
    found = set()
    if isinstance(value, dict):
        found.update(FORBIDDEN_CONTENT_KEYS & value.keys())
        for nested in value.values():
            found.update(_find_forbidden_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(_find_forbidden_keys(nested))
    return found


def _validate_normalized_values(knowledge: KnowledgeBase, source: Path) -> None:
    service_ids = [service.id for service in knowledge.services]
    concept_ids = [concept.id for concept in knowledge.concepts]
    concept_names = [knowledge.canonicalize(concept.name) for concept in knowledge.concepts]
    alias_names = [" ".join(TOKEN_PATTERN.findall(alias.casefold())) for alias, _canonical in knowledge.syntax_aliases]
    if len(service_ids) != len(set(service_ids)):
        raise ValueError(f"Duplicate service IDs in knowledge base: {source}")
    if len(concept_ids) != len(set(concept_ids)) or len(concept_names) != len(set(concept_names)):
        raise ValueError(f"Duplicate concept IDs or names in knowledge base: {source}")
    if len(alias_names) != len(set(alias_names)):
        raise ValueError(f"Duplicate syntax aliases in knowledge base: {source}")
    known_services = set(service_ids)
    unresolved = {
        service_id
        for concept in knowledge.concepts
        for service_id in concept.service_ids
        if service_id not in known_services
    }
    if unresolved:
        raise ValueError(f"Unknown concept service IDs {sorted(unresolved)}: {source}")
    for service in knowledge.services:
        if not service.id or not service.name or not service.tokens or not service.source_url or not service.description:
            raise ValueError(f"Incomplete service {service.id!r}: {source}")
    for concept in knowledge.concepts:
        if not concept.id or not concept.name or not concept.service_ids or not concept.description:
            raise ValueError(f"Incomplete concept {concept.id!r}: {source}")
    for section, rows in (
        ("common_misconceptions", knowledge.common_misconceptions),
        ("must_not_claim", knowledge.must_not_claim),
    ):
        for row in rows:
            if not row.id or not row.key_concepts or not row.source_url:
                raise ValueError(f"Incomplete {section} row {row.id!r}: {source}")
            if len(row.do_not_claim_explanation) != len(row.must_not_claim):
                raise ValueError(f"Mismatched do-not-claim explanations in {section} row {row.id!r}: {source}")
