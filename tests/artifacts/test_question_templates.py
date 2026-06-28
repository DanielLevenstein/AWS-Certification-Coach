import json
from pathlib import Path

import pytest

from aws_certification_coach.question_templates import (
    DEFAULT_QUESTION_TEMPLATE_PATH,
    load_question_templates,
)
from scripts.generate_app_question_artifacts import _build_app_questions


def test_default_question_templates_keep_generation_mechanics_out_of_knowledge_base():
    catalog = load_question_templates()
    template = catalog.get("service-selection-freeform")

    assert catalog.schema_version == 3
    assert template.question_type == "service_selection"
    assert template.prompt_variants
    assert template.option_pattern == "Use {service_name}."
    assert template.option_order == ("correct", "distractor", "distractor", "distractor")
    assert template.selection_rule["correct_option_ids"] == ["A"]
    assert template.distractor_recipes
    assert template.composition_rules["source_url"] == "knowledge_service_source_url"
    assert "source_url" not in template.required_slots
    assert set(template.required_slots) >= {"service_id", "service_name", "purpose"}
    assert len(catalog.service_scenarios) == 40
    assert not hasattr(catalog.service_scenarios[0], "answer_rubric_defaults")


def test_question_templates_own_service_scenarios():
    catalog = load_question_templates()
    scenario = next(scenario for scenario in catalog.service_scenarios if scenario.id == "aws-kms")

    assert scenario.service_id == "kms"
    assert scenario.purpose == "create and manage encryption keys used to protect data in AWS services"
    assert scenario.key_concepts == ("AWS KMS", "encryption keys", "data protection", "key management")
    assert len(scenario.distractors) == 3


def test_question_template_loader_rejects_answer_labels(tmp_path: Path):
    payload = json.loads(DEFAULT_QUESTION_TEMPLATE_PATH.read_text(encoding="utf-8"))
    payload["templates"][0]["rating"] = 0.95
    invalid = tmp_path / "invalid_question_template.json"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="answer-label fields"):
        load_question_templates(invalid)


def test_generated_app_questions_include_template_source_and_normalized_option_metadata():
    questions = _build_app_questions(40)
    lambda_rows = [
        row
        for row in questions
        if any(option["text"] == "Use AWS Lambda." for option in row["original_multiple_choice"]["options"])
    ]

    assert lambda_rows
    lambda_metadata = []
    for row in lambda_rows:
        assert row["question_template_id"] == "service-selection-freeform"
        assert row["source_url"].startswith("https://docs.aws.amazon.com/")
        assert len(row["do_not_claim_explanation"]) == len(row["must_not_claim"])
        for option in row["original_multiple_choice"]["options"]:
            if option["text"] == "Use AWS Lambda.":
                lambda_metadata.append(option["metadata"])

    assert lambda_metadata
    assert {
        (
            metadata["service_id"],
            metadata["service_name"],
            metadata["source_url"],
        )
        for metadata in lambda_metadata
    } == {
        (
            "lambda",
            "AWS Lambda",
            "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
        )
    }
    assert any(
        "AWS Lambda addresses a different AWS need" in feedback
        for row in lambda_rows
        for feedback in row["do_not_claim_explanation"]
    )
    assert any(
        "\n\nAWS Lambda addresses a different AWS need" in feedback
        for row in lambda_rows
        for feedback in row["do_not_claim_explanation"]
    )
