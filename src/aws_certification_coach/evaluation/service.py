"""Evaluation orchestration and development evaluator providers."""

from __future__ import annotations

import json
from typing import Protocol

from dataclasses import replace

from aws_certification_coach.domain import EvaluationResult, Question
from aws_certification_coach.ratings import score_to_letter
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
        result = self.response_parser.parse(response_text)
        return _ensure_actionable_feedback(result, user_answer)


def _ensure_actionable_feedback(result: EvaluationResult, user_answer: str) -> EvaluationResult:
    """Guarantee one useful improvement sentence for every non-A answer."""
    feedback=""
    if score_to_letter(result.score) == "A":
        return result
    if result.score >= 80 and len(user_answer.split()) <= 4:
        feedback = "Please write full sentence answers for full credit."
    elif result.feedback.strip():
        # Add business logic for other types of feedback.
        feedback = result.feedback.strip()
    return replace(result, feedback=feedback)


class HeuristicEvaluatorProvider:
    """Deterministic local evaluator for V1 development and smoke tests."""

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt
        normalized_answer = user_answer.lower()
        matched = [
            concept
            for concept in _required_concepts(question)
            if concept.lower() in normalized_answer
        ]
        missing = [concept for concept in _required_concepts(question) if concept not in matched]
        score = round((len(matched) / max(1, len(_required_concepts(question)))) * 100)
        service_correct = not missing or bool(matched and matched[0] == _required_concepts(question)[0])
        core_concept_correct = not missing
        payload = {
            "score": score,
            "missing_concepts": missing,
            "service_correct": service_correct,
            "core_concept_correct": core_concept_correct,
            "suggested_improvements": [f"Explain {concept}." for concept in missing],
            "detailed_answer": _detailed_answer(question, missing),
        }
        return json.dumps(payload)

def _detailed_answer(question: Question, missing_concepts: list[str]) -> str:
    concept_sentence = ""
    if missing_concepts:
        concept_sentence = " Be sure to explicitly cover: " + ", ".join(missing_concepts) + "."
    return f"{question.reference_answer}{concept_sentence}"


def _required_concepts(question: Question) -> list[str]:
    return question.required_concepts or question.key_concepts
