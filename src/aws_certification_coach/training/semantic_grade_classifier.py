"""Supervised letter-grade classification on normalized semantic embeddings."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from aws_certification_coach.domain import Question
from aws_certification_coach.model_evaluation.grade_metrics import evaluate_letter_predictions


GRADE_SCORES = {"A": 95, "B": 85, "C": 75, "D": 65, "F": 25}
FEATURE_VERSION = "semantic-relations-v2"


class SemanticAnswerFeatureExtractor:
    """Builds normalized answer/reference relationship features."""

    def __init__(self, encoder) -> None:
        self.encoder = encoder

    def extract_many(self, rows: list[tuple[Question, str]]) -> np.ndarray:
        texts = list(
            dict.fromkeys(
                text
                for question, answer in rows
                for text in _semantic_texts(question, answer)
            )
        )
        vectors = np.asarray(
            self.encoder.encode(texts, normalize_embeddings=True),
            dtype=float,
        )
        by_text = dict(zip(texts, vectors, strict=True))
        feature_rows = []
        for question, answer in rows:
            learner = by_text[answer]
            reference_similarity = _cosine(learner, by_text[question.reference_answer])
            acceptable_similarities = [
                _cosine(learner, by_text[value])
                for value in question.acceptable_answers
            ]
            concept_similarities = [
                _cosine(learner, by_text[value])
                for value in (question.required_concepts or question.key_concepts)
            ]
            misconception_similarities = [
                _cosine(learner, by_text[value])
                for value in [*question.common_misconceptions, *question.must_not_claim]
            ]
            correct_similarity = max(
                [reference_similarity, *acceptable_similarities, *concept_similarities]
            )
            incorrect_similarity = max(misconception_similarities, default=0.0)
            feature_rows.append(
                [
                    reference_similarity,
                    max(acceptable_similarities, default=0.0),
                    sum(concept_similarities) / max(1, len(concept_similarities)),
                    min(concept_similarities, default=0.0),
                    incorrect_similarity,
                    correct_similarity - incorrect_similarity,
                    min(2.0, len(answer.split()) / max(1, len(question.reference_answer.split()))),
                    float(_normalized(answer) in {_normalized(value) for value in question.acceptable_answers}),
                ]
            )
        return np.asarray(feature_rows, dtype=float)


@dataclass(frozen=True)
class SemanticGradeClassifier:
    classes: list[str]
    coefficients: list[list[float]]
    intercepts: list[float]
    means: list[float]
    scales: list[float]
    feature_version: str = FEATURE_VERSION

    def predict(self, features: np.ndarray) -> list[str]:
        normalized = (features - np.asarray(self.means)) / np.asarray(self.scales)
        logits = normalized @ np.asarray(self.coefficients).T + np.asarray(self.intercepts)
        indexes = np.argmax(logits, axis=1)
        return [self.classes[int(index)] for index in indexes]

    def save(self, path: str | Path) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "classes": self.classes,
                    "coefficients": self.coefficients,
                    "intercepts": self.intercepts,
                    "means": self.means,
                    "scales": self.scales,
                    "feature_version": self.feature_version,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "SemanticGradeClassifier":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        model = cls(
            classes=[str(value) for value in payload["classes"]],
            coefficients=[[float(value) for value in row] for row in payload["coefficients"]],
            intercepts=[float(value) for value in payload["intercepts"]],
            means=[float(value) for value in payload["means"]],
            scales=[float(value) for value in payload["scales"]],
            feature_version=str(payload["feature_version"]),
        )
        if model.feature_version != FEATURE_VERSION:
            raise ValueError(
                f"Unsupported semantic classifier feature version {model.feature_version!r}; "
                f"expected {FEATURE_VERSION!r}."
            )
        return model


def fit_classifier(features: np.ndarray, labels: list[str]) -> SemanticGradeClassifier:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler().fit(features)
    normalized = scaler.transform(features)
    estimator = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=0,
        solver="lbfgs",
    ).fit(normalized, labels)
    scales = np.where(scaler.scale_ == 0, 1.0, scaler.scale_)
    return SemanticGradeClassifier(
        classes=[str(value) for value in estimator.classes_],
        coefficients=estimator.coef_.tolist(),
        intercepts=estimator.intercept_.tolist(),
        means=scaler.mean_.tolist(),
        scales=scales.tolist(),
    )


def evaluate_classifier(
    classifier: SemanticGradeClassifier,
    features: np.ndarray,
    labels: list[str],
) -> dict[str, object]:
    predictions = classifier.predict(features)
    return evaluate_letter_predictions(labels, predictions)


def _semantic_texts(question: Question, answer: str) -> list[str]:
    return [
        answer,
        question.reference_answer,
        *question.acceptable_answers,
        *(question.required_concepts or question.key_concepts),
        *question.common_misconceptions,
        *question.must_not_claim,
    ]


def _cosine(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.dot(left, right))


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())
