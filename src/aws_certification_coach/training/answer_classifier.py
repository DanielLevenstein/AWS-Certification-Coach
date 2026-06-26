"""Reinforcement-style answer classification model."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
import random

from aws_certification_coach.domain import Question
from aws_certification_coach.training.dataset import (
    AnswerClassificationExample,
    question_signature,
)
from aws_certification_coach.training.features import AnswerFeatureExtractor


@dataclass(frozen=True)
class AnswerClassificationModel:
    feature_names: list[str]
    weights: list[float]
    threshold: float

    def predict_proba(self, features: list[float]) -> float:
        score = sum(weight * value for weight, value in zip(self.weights, features))
        return _sigmoid(score)

    def predict(self, features: list[float]) -> int:
        return 1 if self.predict_proba(features) >= self.threshold else 0

    def save(self, path: str | Path) -> None:
        payload = {
            "feature_names": self.feature_names,
            "weights": self.weights,
            "threshold": self.threshold,
        }
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "AnswerClassificationModel":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            feature_names=[str(name) for name in payload["feature_names"]],
            weights=[float(weight) for weight in payload["weights"]],
            threshold=float(payload["threshold"]),
        )


class ReinforcementAnswerClassifier:
    """Trains a binary answer classifier with policy-gradient rewards."""

    def __init__(
        self,
        feature_extractor: AnswerFeatureExtractor | None = None,
        learning_rate: float = 0.08,
        epochs: int = 500,
        seed: int | None = None,
    ) -> None:
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.seed = seed

    def train(
        self,
        questions: list[Question],
        examples: list[AnswerClassificationExample],
    ) -> AnswerClassificationModel:
        del questions
        rng = random.Random(self.seed) if self.seed is not None else random
        weights = [0.0 for _ in self.feature_extractor.feature_names]
        training_rows = [
            (self.feature_extractor.extract(example.question, example.answer), example.label)
            for example in examples
        ]
        for _ in range(self.epochs):
            rng.shuffle(training_rows)
            for features, label in training_rows:
                probability = _sigmoid(sum(weight * value for weight, value in zip(weights, features)))
                action = 1 if rng.random() < probability else 0
                reward = 1.0 if action == label else -1.0
                gradient_scale = reward * (action - probability)
                weights = [
                    weight + self.learning_rate * gradient_scale * value
                    for weight, value in zip(weights, features)
                ]
        return AnswerClassificationModel(
            feature_names=list(self.feature_extractor.feature_names),
            weights=weights,
            threshold=0.7,
        )


def evaluate_model(
    model: AnswerClassificationModel,
    questions: list[Question],
    examples: list[AnswerClassificationExample],
    feature_extractor: AnswerFeatureExtractor | None = None,
) -> dict[str, float]:
    del questions
    extractor = feature_extractor or AnswerFeatureExtractor()
    correct = 0
    true_positive = false_positive = true_negative = false_negative = 0
    for example in examples:
        prediction = model.predict(extractor.extract(example.question, example.answer))
        correct += int(prediction == example.label)
        true_positive += int(prediction == 1 and example.label == 1)
        false_positive += int(prediction == 1 and example.label == 0)
        true_negative += int(prediction == 0 and example.label == 0)
        false_negative += int(prediction == 0 and example.label == 1)
    total = max(1, len(examples))
    precision = true_positive / max(1, true_positive + false_positive)
    recall = true_positive / max(1, true_positive + false_negative)
    return {
        "accuracy": correct / total,
        "precision": precision,
        "recall": recall,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "false_negative": false_negative,
    }


def evaluate_leave_one_question_out(
    trainer: ReinforcementAnswerClassifier,
    questions: list[Question],
    examples: list[AnswerClassificationExample],
) -> dict[str, float]:
    """Evaluate by holding out every question family in turn."""

    signatures = sorted({question_signature(example.question) for example in examples})
    aggregate = {
        "true_positive": 0,
        "false_positive": 0,
        "true_negative": 0,
        "false_negative": 0,
    }
    total_examples = 0
    correct = 0
    for signature in signatures:
        train_examples = [example for example in examples if question_signature(example.question) != signature]
        held_out_examples = [example for example in examples if question_signature(example.question) == signature]
        if not train_examples or not held_out_examples:
            continue
        model = trainer.train(questions, train_examples)
        metrics = evaluate_model(model, questions, held_out_examples, trainer.feature_extractor)
        held_out_count = len(held_out_examples)
        correct += round(metrics["accuracy"] * held_out_count)
        total_examples += held_out_count
        for key in aggregate:
            aggregate[key] += int(metrics[key])

    if total_examples == 0:
        raise ValueError("Leave-one-question-out evaluation requires examples for at least two questions.")

    return {
        "accuracy": correct / total_examples,
        "precision": aggregate["true_positive"] / max(1, aggregate["true_positive"] + aggregate["false_positive"]),
        "recall": aggregate["true_positive"] / max(1, aggregate["true_positive"] + aggregate["false_negative"]),
        "true_positive": aggregate["true_positive"],
        "false_positive": aggregate["false_positive"],
        "true_negative": aggregate["true_negative"],
        "false_negative": aggregate["false_negative"],
    }


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def answer_calibration_key(question: Question, answer: str) -> str:
    return json.dumps(
        {
            "question": question_signature(question),
            "answer": " ".join(str(answer).casefold().split()),
        },
        sort_keys=True,
    )
