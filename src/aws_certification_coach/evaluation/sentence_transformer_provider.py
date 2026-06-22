"""Local learner-answer evaluator backed by SentenceTransformer embeddings."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Protocol

from aws_certification_coach.config import LocalSemanticModelConfig
from aws_certification_coach.domain import Question
from aws_certification_coach.training.semantic_grade_classifier import (
    GRADE_SCORES,
    SemanticAnswerFeatureExtractor,
    SemanticGradeClassifier,
)


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class Encoder(Protocol):
    def encode(self, sentences: list[str], *, normalize_embeddings: bool) -> object: ...


class SentenceTransformerEvaluatorProvider:
    """Scores answers locally using semantic anchors and structured examples."""

    def __init__(
        self,
        config: LocalSemanticModelConfig | None = None,
        encoder: Encoder | None = None,
        classifier: SemanticGradeClassifier | None = None,
    ) -> None:
        self.config = config or LocalSemanticModelConfig()
        self.device = resolve_device(self.config)
        if encoder is None:
            from sentence_transformers import SentenceTransformer

            model_path = Path(self.config.model_path)
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Local answer model not found at {model_path}. "
                    "Run scripts/download_answer_embedding_model.py first."
                )
            encoder = SentenceTransformer(str(model_path), device=self.device)
        self.encoder = encoder
        self.feature_extractor = SemanticAnswerFeatureExtractor(self.encoder)
        self.classifier = classifier or SemanticGradeClassifier.load(self.config.classifier_path)

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        features = self.feature_extractor.extract_many([(question, user_answer)])
        predicted_grade = self.classifier.predict(features)[0]
        score = GRADE_SCORES[predicted_grade]
        normalized_answer = _normalized(user_answer)
        if normalized_answer in {
            _normalized(value)
            for value in [*question.common_misconceptions, *question.must_not_claim]
        }:
            score = min(score, 49)
        if _normalized(user_answer) in {_normalized(answer) for answer in question.acceptable_answers}:
            score = max(score, 95)

        missing = [
            concept
            for concept in (question.required_concepts or question.key_concepts)
            if _normalized(concept) not in _normalized(user_answer)
        ]
        payload = {
            "score": max(0, min(100, score)),
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": _feedback(score),
            "detailed_answer": question.reference_answer,
        }
        return json.dumps(payload)


def resolve_device(config: LocalSemanticModelConfig) -> str | None:
    """Return CPU for the production override, otherwise allow accelerator auto-selection."""

    if config.cpu_only:
        return "cpu"
    normalized = config.device.strip().casefold()
    return None if normalized in {"", "auto"} else normalized


def _normalized(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.casefold()))


def _feedback(score: int) -> str:
    if score >= 90:
        return "Correct and aligned with the expected AWS concepts."
    if score >= 80:
        return "Mostly correct; add the missing AWS-specific detail for full credit."
    if score >= 60:
        return "Partially correct, but the response needs more precise AWS reasoning."
    return "The response does not yet match the expected AWS service or concept."
