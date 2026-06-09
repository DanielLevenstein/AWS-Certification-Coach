"""Evaluation orchestration and development evaluator providers."""

from __future__ import annotations

import json
from typing import Protocol

from aws_certification_coach.domain import EvaluationResult, Question
from aws_certification_coach.evaluation.prompting import EvaluationPromptBuilder, EvaluationResponseParser


class EvaluatorProvider(Protocol):
    """Provider boundary for any model or scoring implementation."""

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        """Return JSON text matching EvaluationResult fields."""


class EvaluationService:
    """Coordinates prompt creation, provider execution, and response parsing."""

    def __init__(
        self,
        provider: EvaluatorProvider,
        prompt_builder: EvaluationPromptBuilder | None = None,
        response_parser: EvaluationResponseParser | None = None,
    ) -> None:
        self.provider = provider
        self.prompt_builder = prompt_builder or EvaluationPromptBuilder()
        self.response_parser = response_parser or EvaluationResponseParser()

    def evaluate(self, question: Question, user_answer: str) -> EvaluationResult:
        prompt = self.prompt_builder.build(question, user_answer)
        response_text = self.provider.evaluate(prompt, question, user_answer)
        return self.response_parser.parse(response_text)


class HeuristicEvaluatorProvider:
    """Deterministic local evaluator for V1 development and smoke tests."""

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        normalized_answer = user_answer.lower()
        matched = [
            concept
            for concept in question.key_concepts
            if concept.lower() in normalized_answer
        ]
        missing = [concept for concept in question.key_concepts if concept not in matched]
        score = round((len(matched) / max(1, len(question.key_concepts))) * 100)
        payload = {
            "score": score,
            "missing_concepts": missing,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "feedback": _feedback(score),
            "detailed_answer": _detailed_answer(question, missing),
        }
        return json.dumps(payload)


def _feedback(score: int) -> str:
    if score >= 80:
        return "This answer is close. Review the detailed answer below for exam-ready wording."
    if score >= 50:
        return "This answer has part of the idea, but it needs more complete AWS-specific detail."
    return "This answer misses several expected concepts. Use the detailed answer below as the target."


def _detailed_answer(question: Question, missing_concepts: list[str]) -> str:
    concept_sentence = ""
    if missing_concepts:
        concept_sentence = " Be sure to explicitly cover: " + ", ".join(missing_concepts) + "."
    return f"{question.reference_answer}{concept_sentence}"
