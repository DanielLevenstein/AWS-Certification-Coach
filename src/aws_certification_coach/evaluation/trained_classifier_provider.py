"""Evaluator provider backed by the trained answer classification model."""

from __future__ import annotations

import json
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.evaluation.grading import evaluate_with_agents
from aws_certification_coach.training.answer_classifier import AnswerClassificationModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


SUCCESS_THRESHOLD = 70


class TrainedClassifierEvaluatorProvider:
    """Uses the trained classifier to decide whether an answer earns full credit."""

    def __init__(self, model_path: str | Path, feature_extractor: AnswerFeatureExtractor | None = None) -> None:
        self.model = AnswerClassificationModel.load(model_path)
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract(question, user_answer)
        probability = self.model.predict_proba(features)
        model_score = probability * 100
        result = evaluate_with_agents(question, user_answer, evidence_score=model_score)
        payload = {
            "score": result.score,
            "missing_concepts": result.missing_concepts,
            "suggested_improvements": result.suggested_improvements,
            "feedback": result.feedback,
            "detailed_answer": result.detailed_answer,
        }
        return json.dumps(payload)
