"""Factory for configurable evaluation providers."""

from __future__ import annotations

from aws_certification_coach.config import EvaluatorConfig, load_evaluator_config
from aws_certification_coach.evaluation.service import EvaluationService, HeuristicEvaluatorProvider
from aws_certification_coach.evaluation.sentence_transformer_provider import SentenceTransformerEvaluatorProvider
from aws_certification_coach.evaluation.trained_classifier_provider import (
    SemanticSimilarityEvaluatorProvider,
    TrainedClassifierEvaluatorProvider,
    TrainedRegressionEvaluatorProvider,
)
from aws_certification_coach.llm.openai_provider import OpenAIEvaluatorProvider


def build_evaluation_service(config: EvaluatorConfig | None = None) -> EvaluationService:
    evaluator_config = config or load_evaluator_config()
    provider_name = evaluator_config.provider.lower()
    if provider_name == "heuristic":
        provider = HeuristicEvaluatorProvider()
    elif provider_name in {"sentence_transformer", "local_semantic"}:
        provider = SentenceTransformerEvaluatorProvider(evaluator_config.local_semantic)
    elif provider_name == "openai":
        provider = OpenAIEvaluatorProvider(
            evaluator_config.openai,
            structured_answer_data_path=evaluator_config.structured_answer_data_path,
        )
    elif provider_name == "trained_classifier":
        provider = TrainedClassifierEvaluatorProvider(evaluator_config.trained_classifier_model_path)
    elif provider_name in {"semantic_similarity", "semantic_aware"}:
        provider = SemanticSimilarityEvaluatorProvider(
            feedback_paths=evaluator_config.semantic_feedback_paths,
            questions_path=evaluator_config.semantic_questions_path,
        )
    elif provider_name == "trained_regressor":
        provider = TrainedRegressionEvaluatorProvider(evaluator_config.trained_regressor_model_path)
    else:
        raise ValueError(f"Unsupported evaluator provider: {evaluator_config.provider}")
    return EvaluationService(provider)
