from pathlib import Path

from aws_certification_coach.config import EvaluatorConfig
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.dataset import load_answer_classification_examples
from scripts import train_answer_accuracy


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"
TEST_ANSWER_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"


def test_test_verification_artifacts_are_separate_and_large_enough():
    questions = JsonQuestionRepository(TEST_QUESTION_ARTIFACT).all()
    examples = load_answer_classification_examples(TEST_ANSWER_ARTIFACT)

    assert len(questions) >= 8
    assert len(examples) >= 100
    assert all(question.question for question in questions)


def test_training_defaults_only_use_generated_training_split_from_generated_dir():
    generated_defaults = [
        train_answer_accuracy.DEFAULT_GENERATED_TRAINING_DATA,
        train_answer_accuracy.DEFAULT_GENERATED_VALIDATION_DATA,
    ]

    assert generated_defaults == [
        "data/generated/questions_with_answers_training.json",
        "data/generated/questions_with_answers_validation.json",
    ]
    assert all(path.endswith(("questions_with_answers_training.json", "questions_with_answers_validation.json")) for path in generated_defaults)
    assert all(not path.endswith(("generated_feedback.json", "user_feedback.v2.json")) for path in generated_defaults)
    assert train_answer_accuracy.DEFAULT_CURATED_FEEDBACK_DATA == ("data/curated/curated_training_data.json",)
    assert train_answer_accuracy.DEFAULT_CURATED_TRAINING_DIR == "data/curated"
    assert all(path.startswith("data/curated/") for path in train_answer_accuracy.DEFAULT_CURATED_FEEDBACK_DATA)


def test_semantic_feedback_defaults_are_curated_only():
    assert EvaluatorConfig.semantic_feedback_paths == ("data/curated/curated_training_data.json",)
