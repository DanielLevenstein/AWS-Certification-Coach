from pathlib import Path

import json

from aws_certification_coach.questions.json_repository import JsonQuestionRepository, question_from_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"
EXPECTED_EXAM_CODES = {
    "Cloud Practitioner": "CLF-C02",
    "Solutions Architect Associate": "SAA-C03",
    "AWS Certified Developer": "DVA-C02",
}


def test_question_artifact_preserves_original_multiple_choice_provenance():
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()

    assert len(questions) >= 85
    for question in questions:
        original = question.original_multiple_choice
        assert original is not None
        assert original.question
        assert original.options
        assert original.correct_option_ids
        assert original.source_name.startswith("AWS Documentation:")
        assert original.source_url.startswith("https://docs.aws.amazon.com/")


def test_sample_question_artifact_excludes_training_answer_sections():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))
    training_only_fields = {"binary_answers", "wrong_answers", "partial_answers", "generated_answers"}

    assert rows
    assert all(training_only_fields.isdisjoint(row) for row in rows)
    assert all("question" in row for row in rows)
    assert all("reference_answer" in row for row in rows)


def test_sample_question_artifact_includes_exam_code_metadata():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))

    assert rows
    for row in rows:
        assert row.get("exam_code") == EXPECTED_EXAM_CODES[row["certification"]]


def test_sample_question_artifact_includes_answer_rubric_contract():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))
    allowed_question_types = {
        "multiple_choice",
        "scenario_multiple_choice",
        "multi_select_source",
        "service_selection",
        "service_comparison",
        "architecture_tradeoff",
        "artifact_review",
    }
    rubric_fields = {
        "required_concepts",
        "bonus_concepts",
        "common_misconceptions",
        "acceptable_answers",
        "must_not_claim",
    }

    assert rows
    for row in rows:
        assert row.get("question_type") in allowed_question_types
        assert rubric_fields <= set(row)
        assert row["required_concepts"]
        assert row["acceptable_answers"]


def test_existing_question_rows_load_without_rubric_metadata():
    question = question_from_json(
        {
            "certification": "Cloud Practitioner",
            "domain": "Security",
            "difficulty": "Easy",
            "question": "Which service manages encryption keys?",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "key_concepts": ["AWS KMS", "encryption keys"],
        }
    )

    assert question.question_type == "service_selection"
    assert question.required_concepts == ["AWS KMS", "encryption keys"]
    assert question.acceptable_answers == []


def test_sample_question_artifact_includes_developer_question_fidelity_metadata():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))
    developer_rows = [row for row in rows if row.get("exam_code") == "DVA-C02"]

    assert len(developer_rows) >= 5
    assert {row.get("certification") for row in developer_rows} == {"AWS Certified Developer"}
    assert all(row.get("source_examples") for row in developer_rows)
    assert all(row.get("question_fidelity", {}).get("question_fidelity_score", 0) >= 80 for row in developer_rows)


def test_developer_questions_do_not_include_multiple_choice_instructions():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))
    developer_rows = [row for row in rows if row.get("exam_code") == "DVA-C02"]

    assert developer_rows
    assert all("Choose the best answer" not in row["question"] for row in developer_rows)
    assert all(
        "Choose the best answer" not in row["original_multiple_choice"]["question"]
        for row in developer_rows
    )


def test_developer_multiple_choice_options_use_short_service_answers():
    rows = json.loads(QUESTION_ARTIFACT.read_text(encoding="utf-8"))
    developer_rows = [row for row in rows if row.get("exam_code") == "DVA-C02"]

    assert developer_rows
    for row in developer_rows:
        correct_option = next(
            option
            for option in row["original_multiple_choice"]["options"]
            if option["option_id"] in row["original_multiple_choice"]["correct_option_ids"]
        )
        assert len(correct_option["text"]) < len(row["reference_answer"])


def test_combined_training_artifact_keeps_answer_sections_with_questions():
    artifact = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_training.json"
    rows = JsonQuestionRepository(artifact).all()
    raw_rows = json.loads(artifact.read_text(encoding="utf-8"))

    assert len(rows) >= 24
    assert all(row.get("generated_answers") for row in raw_rows)
    assert all(row.get("exam_code") == EXPECTED_EXAM_CODES[row["certification"]] for row in raw_rows)
