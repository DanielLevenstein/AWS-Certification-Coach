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
        model_score = probability * 100
        if _is_incorrect_service_selection(question, user_answer):
            missing = _missing_concepts(question, user_answer)
            payload = {
                "score": min(int(model_score), 50),
                "missing_concepts": missing,
                "suggested_improvements": [f"Explain {concept}." for concept in missing],
                "feedback": (
                    f"Raw model score: {model_score:.2f}%. This exact service answer is not in the "
                    "question's correct answer list."
                ),
                "detailed_answer": question.reference_answer,
            }
            return json.dumps(payload)
        missing = [] if prediction == 1 else _missing_concepts(question, user_answer)
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


def _is_incorrect_service_selection(question: Question, user_answer: str) -> bool:
    original = question.original_multiple_choice
    if original is None:
        return False
    normalized_answer = _normalized(user_answer)
    if not normalized_answer.startswith("use "):
        return False
    if len(normalized_answer.split()) > 6:
        return False
    correct_ids = set(original.correct_option_ids)
    correct_answers = {
        _normalized(option.text)
        for option in original.options
        if option.option_id in correct_ids
    }
    return normalized_answer not in correct_answers


def _feedback(model_score: float, prediction: int) -> str:
    if prediction == 1:
        return f"Model score: {model_score:.2f}%. This answer is above the correctness threshold."
    return f"Model score: {model_score:.2f}%. This answer is below the correctness threshold and needs more AWS-specific detail."


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace(".", "").split())
