from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.dataset import load_answer_classification_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOLDOUT_QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "verification" / "questions" / "transformed_freeform_holdout.json"
HOLDOUT_ANSWER_ARTIFACT = PROJECT_ROOT / "data" / "verification" / "answers" / "answer_classification_holdout.json"


def test_holdout_verification_artifacts_are_separate_and_large_enough():
    questions = JsonQuestionRepository(HOLDOUT_QUESTION_ARTIFACT).all()
    examples = load_answer_classification_examples(HOLDOUT_ANSWER_ARTIFACT)

    assert len(questions) >= 100
    assert len(examples) >= 100
    assert all(question.question_id.startswith("AWS-HOLDOUT") for question in questions)
