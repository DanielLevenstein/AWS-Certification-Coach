from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.answer_classifier import ReinforcementAnswerClassifier, evaluate_leave_one_question_out
from aws_certification_coach.training.dataset import load_answer_classification_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUESTION_ARTIFACT = PROJECT_ROOT / "data" / "questions" / "transformed_freeform_generated.json"
TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "training" / "answer_classification_generated.json"


def test_reinforcement_classifier_exceeds_held_out_accuracy_gate():
    questions = JsonQuestionRepository(QUESTION_ARTIFACT).all()
    questions_by_id = {question.question_id: question for question in questions}
    examples = load_answer_classification_examples(TRAINING_ARTIFACT)

    metrics = evaluate_leave_one_question_out(
        ReinforcementAnswerClassifier(epochs=100, learning_rate=0.08),
        questions_by_id,
        examples,
    )

    assert len(questions) >= 100
    assert len(examples) >= 100
    assert metrics["accuracy"] >= 0.90
