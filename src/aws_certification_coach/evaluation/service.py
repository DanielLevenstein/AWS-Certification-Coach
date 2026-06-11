"""Evaluation orchestration and development evaluator providers."""

from __future__ import annotations

import json
from typing import Protocol

from aws_certification_coach.domain import EvaluationResult, Question
from aws_certification_coach.evaluation.grading import evaluate_with_agents
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
        return self.response_parser.parse(response_text, question)


class HeuristicEvaluatorProvider:
    """Deterministic local evaluator for V1 development and smoke tests."""

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        result = evaluate_with_agents(question, user_answer)
        payload = {
            "score": result.score,
            "missing_concepts": result.missing_concepts,
            "suggested_improvements": result.suggested_improvements,
            "feedback": result.feedback,
            "detailed_answer": result.detailed_answer,
        }
        return json.dumps(payload)
