"""Fast, read-only checks for the configured local answer models."""

from math import isfinite
from pathlib import Path

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.knowledge_base import load_knowledge_base
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRUCTURED_QUESTIONS = JsonQuestionRepository(
    PROJECT_ROOT / "config" / "data" / "structured_answer_training_data.json"
).all()


def _question(fragment: str):
    return next(question for question in STRUCTURED_QUESTIONS if fragment in question.question)


def test_committed_regressor_matches_feature_contract():
    model = AnswerRegressionModel.load(PROJECT_ROOT / "models" / "answer_regressor_model.json")
    extractor = AnswerFeatureExtractor(answer_form=model.answer_form)

    # Older committed regressors remain readable when new features are appended;
    # their named feature prefix must still align exactly with their weights.
    assert model.feature_names == extractor.feature_names[: len(model.feature_names)]
    assert len(model.weights) == len(model.feature_names)
    assert all(isfinite(weight) for weight in model.weights)


def test_knowledge_aliases_produce_equivalent_classifier_features():
    knowledge = load_knowledge_base()
    extractor = AnswerFeatureExtractor(answer_form="both", knowledge_base=knowledge)
    question = _question("managed build project")

    assert extractor.extract(question, "Use AWS Code Build.") == extractor.extract(
        question,
        "Use AWS CodeBuild.",
    )


def test_production_evaluator_orders_representative_answers():
    service = build_evaluation_service()
    question = _question("manages encryption keys")

    correct = service.evaluate(question, "AWS KMS manages encryption keys.").score
    partial = service.evaluate(question, "Encryption keys are important.").score
    incorrect = service.evaluate(question, "Use Amazon S3.").score

    assert correct > partial > incorrect
    assert all(0 <= score <= 100 for score in (correct, partial, incorrect))
    assert all(score_to_letter(score) in {"A", "B", "C", "D", "F"} for score in (correct, partial, incorrect))
