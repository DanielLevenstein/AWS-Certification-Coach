"""Evaluator providers backed by locally trained answer models."""

from __future__ import annotations

import json
from pathlib import Path

from aws_certification_coach.domain import EvaluationResult, Question
from aws_certification_coach.evaluation.grading import evaluate_with_agents
from aws_certification_coach.training.answer_classifier import AnswerClassificationModel, AnswerRegressionModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


SUCCESS_THRESHOLD = 70


class TrainedClassifierEvaluatorProvider:
    """Uses classifier confidence as evidence for the grading agents."""

    def __init__(self, model_path: str | Path, feature_extractor: AnswerFeatureExtractor | None = None) -> None:
        self.model = AnswerClassificationModel.load(model_path)
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract(question, user_answer)
        model_score = self.model.predict_proba(features) * 100
        return _result_json(evaluate_with_agents(question, user_answer, evidence_score=model_score))


class TrainedRegressionEvaluatorProvider:
    """Uses the partial-credit prediction as evidence for the grading agents."""

    def __init__(self, model_path: str | Path, feature_extractor: AnswerFeatureExtractor | None = None) -> None:
        self.model = AnswerRegressionModel.load(model_path)
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract(question, user_answer)
        model_score = self.model.predict(features) * 100
        return _result_json(evaluate_with_agents(question, user_answer, evidence_score=model_score))


def _result_json(result: EvaluationResult) -> str:
    return json.dumps(
        {
            "score": result.score,
            "missing_concepts": result.missing_concepts,
            "suggested_improvements": result.suggested_improvements,
            "feedback": result.feedback,
            "detailed_answer": result.detailed_answer,
        }
    )
