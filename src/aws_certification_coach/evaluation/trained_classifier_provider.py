"""Evaluator provider backed by the trained answer classification model."""

from __future__ import annotations

import json
from pathlib import Path

from aws_certification_coach.domain import Question
from aws_certification_coach.training.answer_classifier import AnswerClassificationModel
from aws_certification_coach.training.features import AnswerFeatureExtractor


class TrainedClassifierEvaluatorProvider:
    """Uses the trained classifier to decide whether an answer earns full credit."""

    def __init__(self, model_path: str | Path, feature_extractor: AnswerFeatureExtractor | None = None) -> None:
        self.model = AnswerClassificationModel.load(model_path)
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract(question, user_answer)
        probability = self.model.predict_proba(features)
        prediction = self.model.predict(features)
        missing = [] if prediction == 1 else _missing_concepts(question, user_answer)
        model_score = probability * 100
        score = int(model_score)
        payload = {
            "score": score,
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": _feedback(model_score, prediction),
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)


def _missing_concepts(question: Question, user_answer: str) -> list[str]:
    normalized_answer = user_answer.casefold()
    return [
        concept
        for concept in question.key_concepts
        if concept.casefold() not in normalized_answer
    ]


def _feedback(model_score: float, prediction: int) -> str:
    if prediction == 1:
        return f"Model score: {model_score:.2f}%. This answer is above the correctness threshold."
    return f"Model score: {model_score:.2f}%. This answer is below the correctness threshold and needs more AWS-specific detail."
