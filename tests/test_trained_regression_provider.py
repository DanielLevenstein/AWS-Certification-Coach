from aws_certification_coach.config import EvaluatorConfig
from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


def test_trained_regressor_config_uses_semantic_aware_application_score(tmp_path):
    feature_names = list(AnswerFeatureExtractor.feature_names)
    model_path = tmp_path / "partial_answer_regressor.json"
    # A bias-only model makes the expected runtime score independent of an answer text.
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
        question="Explain which service manages encryption keys.",
        reference_answer="Use AWS KMS to create and manage encryption keys.",
        key_concepts=["AWS KMS", "encryption keys", "key management"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which service manages encryption keys?",
            options=[
                MultipleChoiceOption("A", "Use AWS KMS."),
                MultipleChoiceOption("B", "Use Amazon S3."),
            ],
            correct_option_ids=["A"],
        ),
    )

    result = service.evaluate(question, "KMS manages encryption keys.")

    assert result.score >= 80
