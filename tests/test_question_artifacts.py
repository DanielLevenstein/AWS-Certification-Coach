from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "sample_questions.json"


def test_question_artifact_preserves_original_multiple_choice_provenance():
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()

    assert len(questions) == 10
    for question in questions:
        original = question.original_multiple_choice
        assert original is not None
        assert original.question
        assert original.options
        assert original.correct_option_ids
