"""Prompt and response helpers for answer evaluation."""

from __future__ import annotations

import json

from aws_certification_coach.domain import EvaluationResult, Question


class EvaluationPromptBuilder:
    """Builds the stable grading prompt used by every evaluator provider."""

    def build(self, question: Question, user_answer: str) -> str:
        concepts = "\n".join(f"- {concept}" for concept in question.key_concepts)
        return f"""Evaluate the learner's answer against the reference answer.

Question:
{question.question}

Reference answer:
{question.reference_answer}

Key concepts:
{concepts}

Learner answer:
{user_answer}

Return JSON only with:
- score: integer from 0 to 100
- missing_concepts: array of strings
- suggested_improvements: array of strings
- feedback: concise learner-facing explanation
- detailed_answer: detailed correct answer that covers the reference answer and every missing concept
"""


class EvaluationResponseParser:
    """Converts provider JSON into an EvaluationResult."""

    def parse(self, response_text: str) -> EvaluationResult:
        payload = json.loads(response_text)
        return EvaluationResult(
            score=_bounded_score(payload.get("score", 0)),
            missing_concepts=_string_list(payload.get("missing_concepts", [])),
            suggested_improvements=_string_list(payload.get("suggested_improvements", [])),
            feedback=str(payload.get("feedback", "")),
            detailed_answer=str(payload.get("detailed_answer", "")),
        )


def _bounded_score(value: object) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]
