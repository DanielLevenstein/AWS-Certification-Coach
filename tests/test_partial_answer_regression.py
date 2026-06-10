from pathlib import Path

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.answer_classifier import PartialCreditRegressor, evaluate_regression_leave_one_question_out
from aws_certification_coach.training.dataset import load_answer_regression_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_generated.json"


def test_partial_credit_regressor_reports_mse_metrics():
    questions = JsonQuestionRepository(TRAINING_ARTIFACT).all()
    questions_by_id = {question.question_id: question for question in questions}
    examples = load_answer_regression_examples(TRAINING_ARTIFACT)

    metrics = evaluate_regression_leave_one_question_out(
        PartialCreditRegressor(epochs=500, learning_rate=0.02),
        questions_by_id,
        examples,
    )

    print(f"partial_regression_metrics mse={metrics['mse']:.3f} mae={metrics['mae']:.3f}")

    assert len(examples) >= 100
    assert metrics["mse"] <= 0.06
