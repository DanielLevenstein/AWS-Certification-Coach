"""Factory for configurable evaluation providers."""

from __future__ import annotations

from aws_certification_coach.config import EvaluatorConfig, load_evaluator_config
from aws_certification_coach.evaluation.service import EvaluationService, HeuristicEvaluatorProvider
from aws_certification_coach.evaluation.trained_classifier_provider import TrainedClassifierEvaluatorProvider
from aws_certification_coach.llm.openai_provider import OpenAIEvaluatorProvider


def build_evaluation_service(config: EvaluatorConfig | None = None) -> EvaluationService:
    evaluator_config = config or load_evaluator_config()
    provider_name = evaluator_config.provider.lower()
    if provider_name == "heuristic":
        provider = HeuristicEvaluatorProvider()
    elif provider_name == "openai":
        provider = OpenAIEvaluatorProvider(evaluator_config.openai)
    elif provider_name == "trained_classifier":
        provider = TrainedClassifierEvaluatorProvider(evaluator_config.trained_classifier_model_path)
    else:
        raise ValueError(f"Unsupported evaluator provider: {evaluator_config.provider}")
    return EvaluationService(provider)
