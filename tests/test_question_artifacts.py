from pathlib import Path

import json

from aws_certification_coach.questions.json_repository import JsonQuestionRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"


def test_question_artifact_preserves_original_multiple_choice_provenance():
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()

    assert len(questions) >= 80
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
    assert all(row["question_id"].startswith("AWS-APP") for row in rows)


def test_combined_training_artifact_keeps_answer_sections_with_questions():
    artifact = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_generated.json"
    rows = JsonQuestionRepository(artifact).all()
    raw_rows = json.loads(artifact.read_text(encoding="utf-8"))

    assert len(rows) >= 100
    assert all(row.get("generated_answers") for row in raw_rows)
