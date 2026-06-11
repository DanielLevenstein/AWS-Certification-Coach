"""Prompt and response helpers for answer evaluation."""

from __future__ import annotations

import json

from aws_certification_coach.domain import EvaluationResult, Question
from aws_certification_coach.evaluation.grading import (
    ConceptCoverageJudgment,
    CorrectnessJudgment,
    EvaluationAggregator,
    WordingJudgment,
)


class EvaluationPromptBuilder:
    """Builds the stable grading prompt used by every evaluator provider."""

    def build(self, question: Question, user_answer: str) -> str:
        concepts = "\n".join(f"- {concept}" for concept in question.key_concepts)
        multiple_choice = _multiple_choice_context(question)
        return f"""Evaluate the learner's answer with three independent grading agents.

Follow GRADING_RUBRIC.md. Do not apply score caps or fixed maximum scores.
For each agent, choose the qualitative rubric level first, explain the evidence for that
level, and then assign the independent numeric score. Do not adjust an agent score to make
the weighted final score reach a desired value.

Question:
{question.question}

Reference answer:
{question.reference_answer}

Key concepts:
{concepts}

Original multiple-choice provenance:
{multiple_choice}

Learner answer:
{user_answer}

Return JSON only with this shape:
{{
  "correctness": {{
    "score": 0,
    "rubric_level": "",
    "correct_option_coverage": [],
    "selected_distractors": [],
    "feedback": ""
  }},
  "concept_coverage": {{
    "score": 0,
    "rubric_level": "",
    "covered_concepts": [],
    "missing_concepts": [],
    "feedback": ""
  }},
  "wording": {{
    "score": 0,
    "rubric_level": "",
    "issues": [],
    "feedback": ""
  }}
}}

Each score is an independent integer from 0 to 100. Correctness judges canonical options
and distractors only. Concept coverage judges required AWS concepts only. Wording judges
clarity only. Exact wording and full sentences are not required for full credit.
"""


class EvaluationResponseParser:
    """Converts provider JSON into an EvaluationResult."""

    def parse(self, response_text: str, question: Question | None = None) -> EvaluationResult:
        payload = json.loads(response_text)
        if question is not None and all(
            isinstance(payload.get(key), dict)
            for key in ("correctness", "concept_coverage", "wording")
        ):
            correctness_payload = payload["correctness"]
            concept_payload = payload["concept_coverage"]
            wording_payload = payload["wording"]
            return EvaluationAggregator().aggregate(
                question,
                CorrectnessJudgment(
                    score=_bounded_score(correctness_payload.get("score", 0)),
                    correct_option_coverage=_string_list(
                        correctness_payload.get("correct_option_coverage", [])
                    ),
                    selected_distractors=_string_list(
                        correctness_payload.get("selected_distractors", [])
                    ),
                    feedback=str(correctness_payload.get("feedback", "")),
                    rubric_level=str(correctness_payload.get("rubric_level", "")),
                ),
                ConceptCoverageJudgment(
                    score=_bounded_score(concept_payload.get("score", 0)),
                    covered_concepts=_string_list(concept_payload.get("covered_concepts", [])),
                    missing_concepts=_string_list(concept_payload.get("missing_concepts", [])),
                    feedback=str(concept_payload.get("feedback", "")),
                    rubric_level=str(concept_payload.get("rubric_level", "")),
                ),
                WordingJudgment(
                    score=_bounded_score(wording_payload.get("score", 0)),
                    issues=_string_list(wording_payload.get("issues", [])),
                    feedback=str(wording_payload.get("feedback", "")),
                    rubric_level=str(wording_payload.get("rubric_level", "")),
                ),
            )
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


def _multiple_choice_context(question: Question) -> str:
    original = question.original_multiple_choice
    if original is None:
        return "No original multiple-choice item is available. Use the reference answer."
    options = "\n".join(f"- {option.option_id}: {option.text}" for option in original.options)
    correct_ids = ", ".join(original.correct_option_ids)
    return f"""Question: {original.question}
Options:
{options}
Canonical correct option IDs: {correct_ids}
Explanation: {original.explanation}"""
