from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.dataset import load_answer_classification_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"
TEST_ANSWER_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"


def test_test_verification_artifacts_are_separate_and_large_enough():
    questions = JsonQuestionRepository(TEST_QUESTION_ARTIFACT).all()
    examples = load_answer_classification_examples(TEST_ANSWER_ARTIFACT)

    assert len(questions) >= 8
    assert len(examples) >= 100
    assert all(question.question for question in questions)
