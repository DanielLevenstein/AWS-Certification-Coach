from aws_certification_coach.config import EvaluatorConfig
from aws_certification_coach.domain import Question
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


def test_trained_regressor_prediction_is_used_as_grading_evidence(tmp_path):
    feature_names = list(AnswerFeatureExtractor.feature_names)
    model_path = tmp_path / "partial_answer_regressor.json"
    # A bias-only model makes the evidence score independent of the answer text.
    AnswerRegressionModel(
        feature_names=feature_names,
        weights=[0.75] + [0.0] * (len(feature_names) - 1),
    ).save(model_path)
    service = build_evaluation_service(
        EvaluatorConfig(
            provider="trained_regressor",
            trained_regressor_model_path=str(model_path),
        )
    )
    question = Question(
        question_id="TEST-001",
        certification="Test",
        domain="Test",
        difficulty="Easy",
        question="Explain the service.",
        reference_answer="Use the expected service.",
        key_concepts=["expected service"],
    )

    result = service.evaluate(question, "A sufficiently specific answer")

    assert result.score == 37
    assert "Final score: 37/100." in result.feedback
