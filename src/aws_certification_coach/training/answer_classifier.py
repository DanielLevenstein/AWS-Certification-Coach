"""Reinforcement-style answer classification model."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import random
from typing import Callable

from aws_certification_coach.domain import Question
from aws_certification_coach.training.dataset import (
    AnswerClassificationExample,
    AnswerRegressionExample,
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


@dataclass(frozen=True)
class AnswerRegressionModel:
    feature_names: list[str]
    weights: list[float]
    calibrations: dict[str, float] = field(default_factory=dict)
    answer_form: str = "long"

    def predict(self, features: list[float]) -> float:
        score = sum(weight * value for weight, value in zip(self.weights, features))
        return max(0.0, min(1.0, score))

    def save(self, path: str | Path) -> None:
        payload = {
            "feature_names": self.feature_names,
            "weights": self.weights,
            "calibrations": self.calibrations,
            "answer_form": self.answer_form,
        }
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "AnswerRegressionModel":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            feature_names=[str(name) for name in payload["feature_names"]],
            weights=[float(weight) for weight in payload["weights"]],
            calibrations={str(key): float(value) for key, value in payload.get("calibrations", {}).items()},
            answer_form=str(payload.get("answer_form", "long")),
        )


class PartialCreditRegressor:
    """Trains continuous partial-credit ratings by minimizing squared error."""

    def __init__(
        self,
        feature_extractor: AnswerFeatureExtractor | None = None,
        learning_rate: float = 0.02,
        epochs: int = 500,
        l2_penalty: float = 0.001,
        seed: int | None = None,
    ) -> None:
        self.feature_extractor = feature_extractor or AnswerFeatureExtractor()
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.l2_penalty = l2_penalty
        self.seed = seed

    def train(
        self,
        questions: list[Question],
        examples: list[AnswerRegressionExample],
    ) -> AnswerRegressionModel:
        model, _history = self.train_with_history(questions, examples)
        return model

    def train_with_history(
        self,
        questions: list[Question],
        examples: list[AnswerRegressionExample],
        evaluation_examples: list[AnswerRegressionExample] | None = None,
        checkpoints: list[int] | None = None,
        checkpoint_evaluator: Callable[[AnswerRegressionModel], dict[str, float]] | None = None,
        model_selector: Callable[[dict[str, float]], tuple[float, ...]] | None = None,
    ) -> tuple[AnswerRegressionModel, list[dict[str, float]]]:
        """Train once and record performance from the evolving model."""

        del questions
        rng = random.Random(self.seed) if self.seed is not None else random
        weights = [0.0 for _ in self.feature_extractor.feature_names]
        training_rows = [
            (self.feature_extractor.extract(example.question, example.answer), example.rating)
            for example in examples
        ]
        evaluation_rows = evaluation_examples if evaluation_examples is not None else examples
        checkpoint_epochs = _training_checkpoints(self.epochs, checkpoints)
        history: list[dict[str, float]] = []
        selected_model: AnswerRegressionModel | None = None
        selected_key: tuple[float, ...] | None = None
        for epoch in range(1, self.epochs + 1):
            rng.shuffle(training_rows)
            for features, rating in training_rows:
                prediction = max(0.0, min(1.0, sum(weight * value for weight, value in zip(weights, features))))
                error = prediction - rating
                weights = [
                    weight - self.learning_rate * ((2 * error * value) + (self.l2_penalty * weight))
                    for weight, value in zip(weights, features)
                ]
            if epoch in checkpoint_epochs:
                model = AnswerRegressionModel(
                    feature_names=list(self.feature_extractor.feature_names),
                    weights=list(weights),
                    answer_form=self.feature_extractor.answer_form,
                )
                metrics = evaluate_regression_model(
                    model,
                    [],
                    evaluation_rows,
                    self.feature_extractor,
                )
                if checkpoint_evaluator is not None:
                    metrics.update(checkpoint_evaluator(model))
                history.append({"epoch": epoch, **metrics})
                if model_selector is not None:
                    candidate_key = model_selector(metrics)
                    if selected_key is None or candidate_key > selected_key:
                        selected_key = candidate_key
                        selected_model = model
        return selected_model or model, history


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


def evaluate_regression_model(
    model: AnswerRegressionModel,
    questions: list[Question],
    examples: list[AnswerRegressionExample],
    feature_extractor: AnswerFeatureExtractor | None = None,
) -> dict[str, float]:
    del questions
    extractor = feature_extractor or AnswerFeatureExtractor()
    squared_error = 0.0
    absolute_error = 0.0
    for example in examples:
        prediction = model.predict(extractor.extract(example.question, example.answer))
        error = prediction - example.rating
        squared_error += error * error
        absolute_error += abs(error)
    total = max(1, len(examples))
    return {
        "mse": squared_error / total,
        "mae": absolute_error / total,
        "example_count": len(examples),
    }


def evaluate_regression_leave_one_question_out(
    trainer: PartialCreditRegressor,
    questions: list[Question],
    examples: list[AnswerRegressionExample],
) -> dict[str, float]:
    signatures = sorted({question_signature(example.question) for example in examples})
    squared_error = 0.0
    absolute_error = 0.0
    total_examples = 0
    for signature in signatures:
        train_examples = [example for example in examples if question_signature(example.question) != signature]
        held_out_examples = [example for example in examples if question_signature(example.question) == signature]
        if not train_examples or not held_out_examples:
            continue
        model = trainer.train(questions, train_examples)
        metrics = evaluate_regression_model(model, questions, held_out_examples, trainer.feature_extractor)
        held_out_count = len(held_out_examples)
        squared_error += metrics["mse"] * held_out_count
        absolute_error += metrics["mae"] * held_out_count
        total_examples += held_out_count

    if total_examples == 0:
        raise ValueError("Leave-one-question-out evaluation requires examples for at least two questions.")

    return {
        "mse": squared_error / total_examples,
        "mae": absolute_error / total_examples,
        "example_count": total_examples,
    }


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1 / (1 + z)
    z = math.exp(value)
    return z / (1 + z)


def _training_checkpoints(epochs: int, checkpoints: list[int] | None) -> set[int]:
    requested = checkpoints or [1, 5, 10, 25, 50, 100, 250, 500]
    valid = {epoch for epoch in requested if 1 <= epoch <= epochs}
    valid.add(epochs)
    return valid


def answer_calibration_key(question: Question, answer: str) -> str:
    return json.dumps(
        {
            "question": question_signature(question),
            "answer": " ".join(str(answer).casefold().split()),
        },
        sort_keys=True,
    )
