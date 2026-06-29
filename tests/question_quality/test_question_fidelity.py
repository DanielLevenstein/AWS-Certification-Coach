from pathlib import Path
import json

from aws_certification_coach.question_fidelity.model import QuestionFidelityModel, evaluate_question_batch
from scripts.download_developer_original_questions import SOURCE_ROWS
from scripts.generate_developer_question_artifacts import build_questions


def test_question_fidelity_model_scores_concept_match_without_answer_evaluator():
    source = SOURCE_ROWS[0]
    generated = build_questions([source])[0]

    score = QuestionFidelityModel().score(source, generated)

    assert score.question_fidelity_score >= 80
    assert "dead-letter queue" in score.covered_concepts
    assert score.conflicting_concepts == []
    assert score.review_recommendation in {"accept", "revise"}


def test_question_fidelity_rejects_wrong_service_conflict():
    source = SOURCE_ROWS[2]
    generated = build_questions([source])[0]
    generated["key_concepts"] = ["Amazon S3", "object storage"]
    generated["reference_answer"] = "Use Amazon S3 object storage."
    generated["original_multiple_choice"]["options"][1]["text"] = "Use Amazon S3."

    score = QuestionFidelityModel().score(source, generated)

    assert score.question_fidelity_score < 80
    assert score.review_recommendation == "reject"


def test_question_fidelity_batch_reports_0_to_100_metric():
    sources = SOURCE_ROWS[:2]
    generated = build_questions(sources)

    metrics = evaluate_question_batch(sources, generated)

    assert 0 <= metrics["question_fidelity"] <= 100
    assert metrics["sample_count"] == 2
    assert metrics["source_count"] == 2
    assert metrics["generated_question_count"] == 2
    assert metrics["model_name"] == "question_fidelity_heuristic_v1"


def test_question_fidelity_batch_excludes_disabled_artifact_review_questions(monkeypatch):
    service_source = SOURCE_ROWS[0]
    artifact_source = next(row for row in SOURCE_ROWS if row["source_id"] == "dva-artifact-sdk-pagination")
    sources = [service_source, artifact_source]
    generated = build_questions(sources)

    monkeypatch.delenv("SHOW_ARTIFACT_REVIEW", raising=False)
    metrics = evaluate_question_batch(sources, generated)

    assert metrics["sample_count"] == 1
    assert metrics["source_count"] == 1
    assert metrics["generated_question_count"] == 1

    monkeypatch.setenv("SHOW_ARTIFACT_REVIEW", "1")
    metrics = evaluate_question_batch(sources, generated)

    assert metrics["sample_count"] == 2
    assert metrics["source_count"] == 2
    assert metrics["generated_question_count"] == 2


def test_developer_question_artifact_preserves_source_examples(tmp_path: Path):
    sources = SOURCE_ROWS[:1]
    generated = build_questions(sources)
    output = tmp_path / "developer_question_expansion.json"
    output.write_text(json.dumps(generated, indent=2), encoding="utf-8")

    row = json.loads(output.read_text(encoding="utf-8"))[0]

    assert row["certification"] == "AWS Certified Developer"
    assert row["exam_code"] == "DVA-C02"
    assert row["source_examples"] == [sources[0]["source_id"]]
    assert row["question_fidelity"]["question_fidelity_score"] >= 80
    assert row["original_multiple_choice"]["source_url"].startswith("https://docs.aws.amazon.com/")


def test_developer_question_options_include_normalized_known_service_metadata():
    source = next(row for row in SOURCE_ROWS if row["source_id"] == "dva-secrets-manager-rotation")
    row = build_questions([source])[0]
    correct_option = next(
        option
        for option in row["original_multiple_choice"]["options"]
        if option["option_id"] in row["original_multiple_choice"]["correct_option_ids"]
    )

    assert correct_option["metadata"] == {
        "service_id": "secretsmanager",
        "service_name": "AWS Secrets Manager",
        "source_url": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html",
    }


def test_artifact_review_generation_preserves_artifact_contract():
    source = next(row for row in SOURCE_ROWS if row["source_id"] == "dva-artifact-sdk-pagination")
    row = build_questions([source])[0]

    assert row["question_type"] == "artifact_review"
    assert row["difficulty"] == "Hard"
    assert row["artifact_type"] == "sdk_usage"
    assert row["artifact_language"] == "python"
    assert "list_objects_v2" in row["artifact_body"]
    assert "get_paginator" in row["artifact_corrected"]
    assert row["expected_issue"]
    assert row["question_fidelity"]["question_fidelity_score"] >= 80
