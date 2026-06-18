from aws_certification_coach.config import EvaluatorConfig
from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.trained_classifier_provider import SemanticSimilarityEvaluatorProvider
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


def test_trained_regressor_config_uses_saved_regression_model(tmp_path):
    feature_names = list(AnswerFeatureExtractor.feature_names)
    model_path = tmp_path / "answer_regressor_model.json"
    # A bias-only model makes the runtime score prove the saved regressor was used.
    AnswerRegressionModel(
        feature_names=feature_names,
        weights=[0.42] + [0.0] * (len(feature_names) - 1),
    ).save(model_path)
    service = build_evaluation_service(
        EvaluatorConfig(
            provider="trained_regressor",
            trained_regressor_model_path=str(model_path),
        )
    )
    question = Question(
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

    assert result.score == 42


def test_semantic_similarity_provider_applies_feedback_calibration(tmp_path):
    question = _question()
    feedback_path = tmp_path / "curated_training_data.json"
    feedback_path.write_text(
        """
        [
          {
            "question": "Explain which service manages encryption keys.",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "answer_given": "Near miss answer",
            "correct_rating": "C",
            "rating_given": "F",
            "feedback_text": "This should receive partial credit."
          }
        ]
        """,
        encoding="utf-8",
    )
    provider = SemanticSimilarityEvaluatorProvider(
        feedback_paths=[str(feedback_path)],
        questions=[question],
    )
    service = build_evaluation_service(EvaluatorConfig(provider="semantic_similarity"))
    service.provider = provider

    result = service.evaluate(question, "Near miss answer")

    assert result.score == 75


def test_semantic_similarity_config_uses_feedback_paths(tmp_path):
    question = _question()
    questions_path = tmp_path / "questions.json"
    feedback_path = tmp_path / "curated_training_data.json"
    questions_path.write_text(
        """
        [
          {
            "certification": "Test",
            "domain": "Test",
            "difficulty": "Easy",
            "question": "Explain which service manages encryption keys.",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "key_concepts": ["AWS KMS", "encryption keys", "key management"],
            "original_multiple_choice": {
              "question": "Which service manages encryption keys?",
              "options": [
                {"option_id": "A", "text": "Use AWS KMS."},
                {"option_id": "B", "text": "Use Amazon S3."}
              ],
              "correct_option_ids": ["A"]
            }
          }
        ]
        """,
        encoding="utf-8",
    )
    feedback_path.write_text(
        """
        [
          {
            "question": "Explain which service manages encryption keys.",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "answer_given": "Near miss answer",
            "correct_rating": "C",
            "rating_given": "F"
          }
        ]
        """,
        encoding="utf-8",
    )
    service = build_evaluation_service(
        EvaluatorConfig(
            provider="semantic_similarity",
            semantic_feedback_paths=(str(feedback_path),),
            semantic_questions_path=str(questions_path),
        )
    )

    result = service.evaluate(question, "Near miss answer")

    assert result.score == 75


def _question() -> Question:
    return Question(
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
