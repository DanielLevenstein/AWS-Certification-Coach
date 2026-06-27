from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.recreate_mongo_database import MIGRATED_SCHEMA_VERSION, SourceFiles, build_collection_documents


def test_build_collection_documents_combines_misconception_sources() -> None:
    collections = build_collection_documents(SourceFiles())

    assert collections["content_manifests"][0]["schema_version"] == MIGRATED_SCHEMA_VERSION
    assert collections["content_manifests"][0]["source_schema_version"] == 3
    assert len(collections["misconceptions"]) == 6
    assert "must_not_claim_profiles" not in collections
    assert "misconception_profiles" not in collections


def test_build_collection_documents_preserves_source_payload_fields() -> None:
    collections = build_collection_documents(SourceFiles())

    assert len(collections["question_templates"]) == 1
    assert len(collections["service_scenarios"]) == 40
    assert len(collections["developer_question_scenarios"]) == 38
    assert len(collections["generated_questions"]) >= 198
    assert len([row for row in collections["generated_questions"] if row.get("exam_code") == "DVA-C02"]) == 38

    service = collections["services"][0]
    assert service["_id"] == service["id"]
    assert "source_order" not in service

    structured_example = collections["structured_answer_training_examples"][0]
    assert "_id" in structured_example
    assert "schema_version" not in structured_example

    feedback = collections["user_feedback"][0]
    assert feedback["schema_version"] == 3


def test_question_templates_collection_has_one_document_per_template(tmp_path: Path) -> None:
    question_template = json.loads(Path("config/question_templates/question_template.json").read_text(encoding="utf-8"))
    second_template = {**question_template["templates"][0], "id": "second-template"}
    question_template["templates"] = [question_template["templates"][0], second_template]
    question_template_path = tmp_path / "question_template.json"
    question_template_path.write_text(json.dumps(question_template), encoding="utf-8")

    collections = build_collection_documents(SourceFiles(question_template=question_template_path))

    assert [template["_id"] for template in collections["question_templates"]] == [
        "service-selection-freeform",
        "second-template",
    ]
    assert all("templates" not in template for template in collections["question_templates"])


def test_question_scenario_collections_keep_distinct_schemas() -> None:
    collections = build_collection_documents(SourceFiles())

    service_scenario = collections["service_scenarios"][0]
    developer_scenario = collections["developer_question_scenarios"][0]

    assert {
        "_id",
        "id",
        "service_id",
        "domain",
        "certification",
        "exam_code",
        "difficulty",
        "purpose",
        "key_concepts",
        "distractors",
    } == set(service_scenario)
    assert {
        "_id",
        "id",
        "generated_question",
        "correct_option",
        "reference_answer",
        "distractors",
    } == set(developer_scenario)


def test_build_collection_documents_rejects_diverged_misconception_sources(tmp_path: Path) -> None:
    knowledge_base = json.loads(Path("config/knowledge_base/knowledge_base.json").read_text(encoding="utf-8"))
    knowledge_base["must_not_claim"] = knowledge_base["must_not_claim"][:-1]
    invalid_knowledge_base = tmp_path / "knowledge_base.json"
    invalid_knowledge_base.write_text(json.dumps(knowledge_base), encoding="utf-8")

    sources = SourceFiles(knowledge_base=invalid_knowledge_base)

    with pytest.raises(ValueError, match="common_misconceptions and knowledge_base.must_not_claim"):
        build_collection_documents(sources)
