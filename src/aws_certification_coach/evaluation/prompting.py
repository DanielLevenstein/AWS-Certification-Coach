"""Prompt and response helpers for answer evaluation."""

from __future__ import annotations

import json

from aws_certification_coach.domain import EvaluationResult, Question


class EvaluationPromptBuilder:
    """Builds the stable grading prompt used by every evaluator provider."""

    def build(self, question: Question, user_answer: str) -> str:
        concepts = "\n".join(f"- {concept}" for concept in question.key_concepts)
        required_concepts = "\n".join(f"- {concept}" for concept in _required_concepts(question))
        bonus_concepts = "\n".join(f"- {concept}" for concept in question.bonus_concepts) or "- None"
        acceptable_answers = "\n".join(f"- {answer}" for answer in question.acceptable_answers) or "- None"
        common_misconceptions = "\n".join(f"- {concept}" for concept in question.common_misconceptions) or "- None"
        must_not_claim = "\n".join(f"- {claim}" for claim in question.must_not_claim) or "- None"
        return f"""Evaluate the learner's answer against the reference answer.

Question type:
{question.question_type}

Question:
{question.question}

Reference answer:
{question.reference_answer}

Key concepts:
{concepts}

Required rubric concepts:
{required_concepts}

Bonus concepts:
{bonus_concepts}

Acceptable answers:
{acceptable_answers}

Common misconceptions:
{common_misconceptions}

Must not claim:
{must_not_claim}

Learner answer:
{user_answer}

Scoring scale:
- 90-100 (A): correct service or pattern, core reasoning and constraints covered, no major misconception
- 80-89 (B): mostly correct but missing one meaningful detail, constraint, or tradeoff
- 70-79 (C): partially correct or plausible adjacent solution that misses the best-fit reasoning
- 60-69 (D): minimal relevant credit but fails the main requirement or is too incomplete to trust
- 0-59 (F): wrong service category, contradiction, severe misconception, or no meaningful answer

Judge semantic meaning rather than exact wording. A concise answer can receive full credit when it
unambiguously identifies the correct AWS service or feature and satisfies the question's requested scope.

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


def _required_concepts(question: Question) -> list[str]:
    return question.required_concepts or question.key_concepts
