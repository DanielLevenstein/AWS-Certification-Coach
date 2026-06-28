import json
from pathlib import Path

import pytest

from aws_certification_coach.question_templates import (
    DEFAULT_QUESTION_TEMPLATE_PATH,
    load_question_templates,
)
from scripts.generate_app_question_artifacts import _build_app_questions
from scripts.generate_developer_question_artifacts import build_questions
from scripts.download_developer_original_questions import SOURCE_ROWS


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
    assert catalog.service_scenarios
    assert len({scenario.id for scenario in catalog.service_scenarios}) == len(catalog.service_scenarios)
    assert all(scenario.service_id for scenario in catalog.service_scenarios)
    assert all(scenario.purpose for scenario in catalog.service_scenarios)
    assert all(scenario.key_concepts for scenario in catalog.service_scenarios)
    assert all(len(scenario.distractors) >= 3 for scenario in catalog.service_scenarios)
    assert len(catalog.developer_question_scenarios) == 38
    assert not hasattr(catalog.service_scenarios[0], "answer_rubric_defaults")


def test_question_templates_own_service_scenarios():
    catalog = load_question_templates()
    scenario = next(scenario for scenario in catalog.service_scenarios if scenario.id == "aws-kms")

    assert scenario.service_id == "kms"
    assert scenario.purpose == "create and manage encryption keys used to protect data in AWS services"
    assert scenario.key_concepts == ("AWS KMS", "encryption keys", "data protection", "key management")
    assert len(scenario.distractors) == 3


def test_question_templates_own_developer_question_details_without_aws_source_fields():
    catalog = load_question_templates()
    scenario = next(
        scenario
        for scenario in catalog.developer_question_scenarios
        if scenario.id == "dva-secrets-manager-rotation"
    )

    assert scenario.generated_question.startswith("A developer must keep application database passwords")
    assert scenario.correct_option == "Use AWS Secrets Manager."
    assert scenario.reference_answer.startswith("Use AWS Secrets Manager to store database credentials")
    assert len(scenario.distractors) == 3
    assert not hasattr(scenario, "source_url")
    assert not hasattr(scenario, "services")
    assert not hasattr(scenario, "key_concepts")


def test_developer_generator_uses_question_template_details_before_source_overrides():
    source = dict(SOURCE_ROWS[12])
    source["generated_question"] = "Source override should not win."
    source["correct_option"] = "Source correct option should not win."
    source["reference_answer"] = "Source reference answer should not win."
    source["distractors"] = [
        "Source distractor one.",
        "Source distractor two.",
        "Source distractor three.",
    ]

    row = build_questions([source])[0]

    assert row["question"].startswith("A production Lambda function can overwhelm")
    assert row["reference_answer"].startswith("Configure Lambda reserved concurrency")
    assert row["original_multiple_choice"]["options"][0]["text"] == "Configure Lambda reserved concurrency."


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


def test_generated_app_questions_expand_sns_sqs_boundary_cases():
    questions = _build_app_questions(len(load_question_templates().service_scenarios))
    rows_by_concepts = {
        tuple(row["key_concepts"]): row
        for row in questions
    }

    sns_row = rows_by_concepts[
        ("SNS", "pub/sub", "fanout", "subscribers", "SQS queue polling")
    ]
    sqs_row = rows_by_concepts[
        ("SQS", "message queue", "queue polling", "worker processing", "decoupling")
    ]

    assert sns_row["certification"] == "AWS Certified Developer"
    assert sns_row["exam_code"] == "DVA-C02"
    assert "multiple independent subscribers" in sns_row["question"]
    assert sns_row["reference_answer"].startswith("Use Amazon SNS")
    assert any(
        "Amazon SQS worker queue only is the best fit" in misconception
        for misconception in sns_row["common_misconceptions"]
    )

    assert sqs_row["certification"] == "AWS Certified Developer"
    assert sqs_row["exam_code"] == "DVA-C02"
    assert "competing worker processes" in sqs_row["question"]
    assert sqs_row["reference_answer"].startswith("Use Amazon SQS")
    assert any(
        "Amazon SNS fanout topic only is the best fit" in misconception
        for misconception in sqs_row["common_misconceptions"]
    )


def test_generated_app_questions_expand_ec2_scaling_boundary_case():
    questions = _build_app_questions(len(load_question_templates().service_scenarios))
    rows_by_concepts = {
        tuple(row["key_concepts"]): row
        for row in questions
    }

    row = rows_by_concepts[
        ("Auto Scaling", "EC2", "horizontal scaling", "vertical scaling", "instance replacement")
    ]

    assert row["certification"] == "Solutions Architect Associate"
    assert row["exam_code"] == "SAA-C03"
    assert "horizontally scale an EC2 application" in row["question"]
    assert "larger instance type" in row["question"]
    assert row["reference_answer"].startswith("Use Auto Scaling groups")
    assert any(
        "manual vertical scaling to a larger instance type is the best fit" in misconception
        for misconception in row["common_misconceptions"]
    )


def test_generated_app_questions_expand_s3_lifecycle_bucket_policy_boundary_case():
    questions = _build_app_questions(len(load_question_templates().service_scenarios))
    rows_by_concepts = {
        tuple(row["key_concepts"]): row
        for row in questions
    }

    row = rows_by_concepts[
        (
            "S3 Lifecycle",
            "bucket policies",
            "storage class transitions",
            "object expiration",
            "access permissions",
        )
    ]

    assert row["certification"] == "Solutions Architect Associate"
    assert row["exam_code"] == "SAA-C03"
    assert "lower-cost storage classes" in row["question"]
    assert "without changing bucket access permissions" in row["question"]
    assert row["reference_answer"].startswith("Use S3 lifecycle policies")
    assert any(
        "S3 bucket policy only is the best fit" in misconception
        for misconception in row["common_misconceptions"]
    )
