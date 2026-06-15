from aws_certification_coach.domain import Question
from aws_certification_coach.training.answer_classifier import PartialCreditRegressor
from aws_certification_coach.training.dataset import AnswerRegressionExample


def test_regressor_records_metrics_at_requested_training_checkpoints():
    question = Question(
        question_id="Q1",
        certification="Test",
        domain="Test",
        difficulty="Easy",
        question="Name the service.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
    )
    examples = [
        AnswerRegressionExample("Q1", "Use AWS KMS.", 0.95),
        AnswerRegressionExample("Q1", "AWS", 0.25),
    ]

    model, history = PartialCreditRegressor(epochs=5, seed=0).train_with_history(
        {"Q1": question},
        examples,
        checkpoints=[1, 3, 5],
        checkpoint_evaluator=lambda _model: {"curated_grade_accuracy": 0.5},
    )

    assert [point["epoch"] for point in history] == [1, 3, 5]
    assert all(point["example_count"] == 2 for point in history)
    assert all(point["curated_grade_accuracy"] == 0.5 for point in history)
    assert model.feature_names
