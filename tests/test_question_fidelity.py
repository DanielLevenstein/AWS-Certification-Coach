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


def test_developer_question_artifact_preserves_source_examples(tmp_path: Path):
    sources = SOURCE_ROWS[:1]
    generated = build_questions(sources)
    output = tmp_path / "developer_question_expansion.json"
    output.write_text(json.dumps(generated, indent=2), encoding="utf-8")

    row = json.loads(output.read_text(encoding="utf-8"))[0]

    assert row["certification"] == "AWS Certified Developer - Associate"
    assert row["source_examples"] == [sources[0]["source_id"]]
    assert row["question_fidelity"]["question_fidelity_score"] >= 80
    assert row["original_multiple_choice"]["source_url"].startswith("https://docs.aws.amazon.com/")
