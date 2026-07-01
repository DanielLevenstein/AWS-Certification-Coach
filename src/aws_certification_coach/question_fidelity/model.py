"""Deterministic concept-fidelity model for generated questions.

This module intentionally does not import or reuse answer-grading model code.
It scores generated question artifacts against source concept bundles and
exam-style calibration metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from statistics import mean
from typing import Iterable

from aws_certification_coach.questions.visibility import visible_question_rows


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
DEFAULT_WEIGHTS = {
    "concept_fidelity": 0.35,
    "exam_style": 0.25,
    "distractor_quality": 0.15,
    "technical_correctness": 0.15,
    "source_safety": 0.10,
}
REASONING_TERMS = {
    "application",
    "deploy",
    "deployment",
    "environment",
    "failure",
    "latency",
    "least",
    "monitor",
    "pipeline",
    "request",
    "requirement",
    "secure",
    "serverless",
    "troubleshoot",
    "workflow",
}
COPYING_TOKEN_LIMIT = 0.92


@dataclass(frozen=True)
class QuestionFidelityScore:
    question_fidelity_score: int
    concept_fidelity_score: int
    exam_style_score: int
    distractor_quality_score: int
    technical_correctness_score: int
    source_safety_score: int
    covered_concepts: list[str]
    missing_concepts: list[str]
    conflicting_concepts: list[str]
    matched_exam_style_pattern: str
    distractor_notes: str
    copying_risk_notes: str
    review_recommendation: str
    notes: str


class QuestionFidelityModel:
    """Separate heuristic model for generated-question concept fidelity."""

    model_name = "question_fidelity_heuristic_v1"
    score_threshold = 80

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS

    def score(self, source: dict[str, object], generated: dict[str, object]) -> QuestionFidelityScore:
        source_concepts = _string_list(source.get("concepts", []))
        generated_concepts = _string_list(generated.get("key_concepts", []))
        source_services = _string_list(source.get("services", []))
        question_text = str(generated.get("question", ""))
        reference_answer = str(generated.get("reference_answer", ""))
        combined_text = " ".join([question_text, reference_answer, " ".join(generated_concepts)])
        combined_tokens = _tokens(combined_text)

        covered = [concept for concept in source_concepts if _concept_present(concept, combined_tokens)]
        missing = [concept for concept in source_concepts if concept not in covered]
        conflicts = _conflicting_concepts(source_services, generated_concepts, generated.get("original_multiple_choice", {}))

        concept_score = round(100 * len(covered) / max(1, len(source_concepts)))
        if conflicts:
            concept_score = min(concept_score, 60)

        exam_style_score, matched_style = _exam_style_score(source, generated, question_text)
        distractor_score, distractor_notes = _distractor_quality(generated)
        technical_score = _technical_correctness_score(source_services, reference_answer, conflicts)
        source_safety_score, copying_notes = _source_safety_score(source, question_text)
        total = round(
            concept_score * self.weights["concept_fidelity"]
            + exam_style_score * self.weights["exam_style"]
            + distractor_score * self.weights["distractor_quality"]
            + technical_score * self.weights["technical_correctness"]
            + source_safety_score * self.weights["source_safety"]
        )
        recommendation = _recommendation(total, conflicts, missing, source_safety_score)
        return QuestionFidelityScore(
            question_fidelity_score=_clamp(total),
            concept_fidelity_score=_clamp(concept_score),
            exam_style_score=_clamp(exam_style_score),
            distractor_quality_score=_clamp(distractor_score),
            technical_correctness_score=_clamp(technical_score),
            source_safety_score=_clamp(source_safety_score),
            covered_concepts=covered,
            missing_concepts=missing,
            conflicting_concepts=conflicts,
            matched_exam_style_pattern=matched_style,
            distractor_notes=distractor_notes,
            copying_risk_notes=copying_notes,
            review_recommendation=recommendation,
            notes=f"{len(covered)}/{len(source_concepts)} source concepts covered.",
        )


def evaluate_question_batch(sources: Iterable[dict[str, object]], generated_questions: Iterable[dict[str, object]]) -> dict[str, object]:
    generated_rows = visible_question_rows(generated for generated in generated_questions if isinstance(generated, dict))
    visible_source_ids = {
        source_id
        for generated in generated_rows
        for source_id in _string_list(generated.get("source_examples", []))
    }
    source_by_id = {
        str(source["source_id"]): source
        for source in sources
        if isinstance(source, dict) and str(source.get("source_id", "")) in visible_source_ids
    }
    model = QuestionFidelityModel()
    scored_rows = []
    for generated in generated_rows:
        source_ids = _string_list(generated.get("source_examples", []))
        if not source_ids:
            raise ValueError("Generated question is missing source_examples.")
        source_id = source_ids[0]
        source = source_by_id[source_id]
        score = model.score(source, generated)
        scored_rows.append(score)
    if not scored_rows:
        raise ValueError("No generated questions available for question-fidelity evaluation.")
    average_fidelity = mean(row.question_fidelity_score for row in scored_rows)
    average_concept = mean(row.concept_fidelity_score for row in scored_rows)
    average_exam_style = mean(row.exam_style_score for row in scored_rows)
    return {
        "model_name": model.model_name,
        "question_fidelity": round(average_fidelity, 2),
        "question_concept_fidelity": round(average_concept, 2),
        "question_exam_style_fidelity": round(average_exam_style, 2),
        "threshold": model.score_threshold,
        "sample_count": len(scored_rows),
        "source_count": len(source_by_id),
        "generated_question_count": len(scored_rows),
        "accept_count": sum(1 for row in scored_rows if row.review_recommendation == "accept"),
        "revise_count": sum(1 for row in scored_rows if row.review_recommendation == "revise"),
        "reject_count": sum(1 for row in scored_rows if row.review_recommendation == "reject"),
    }


def _tokens(value: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(value.casefold()))


def _concept_present(concept: str, tokens: set[str]) -> bool:
    concept_tokens = _tokens(concept)
    if not concept_tokens:
        return False
    return len(concept_tokens & tokens) / len(concept_tokens) >= 0.6


def _conflicting_concepts(
    source_services: list[str],
    generated_concepts: list[str],
    original_multiple_choice: object,
) -> list[str]:
    source_tokens = set().union(*(_tokens(service) for service in source_services)) if source_services else set()
    conflicts: list[str] = []
    original = original_multiple_choice if isinstance(original_multiple_choice, dict) else {}
    options = original.get("options", [])
    correct_option_ids = set(_string_list(original.get("correct_option_ids", [])))
    distractor_text = " ".join(
        str(option.get("text", ""))
        for option in options
        if isinstance(option, dict) and str(option.get("option_id", "")) not in correct_option_ids
    )
    distractor_tokens = _tokens(distractor_text)
    for concept in generated_concepts:
        concept_tokens = _tokens(concept)
        if concept_tokens and concept_tokens <= distractor_tokens and not concept_tokens & source_tokens:
            conflicts.append(concept)
    return conflicts


def _exam_style_score(source: dict[str, object], generated: dict[str, object], question_text: str) -> tuple[int, str]:
    notes = str(source.get("exam_style_notes", ""))
    reasoning_pattern = str(source.get("reasoning_pattern", ""))
    difficulty = str(generated.get("difficulty", "")).casefold()
    tokens = _tokens(" ".join([question_text, notes, reasoning_pattern]))
    score = 55
    if tokens & REASONING_TERMS:
        score += 20
    if "developer" in str(generated.get("certification", "")).casefold():
        score += 10
    if difficulty in {"medium", "hard"}:
        score += 10
    if "best" in tokens or "which" in tokens:
        score += 5
    pattern = reasoning_pattern or notes or "Developer Associate scenario reasoning"
    return _clamp(score), pattern


def _distractor_quality(generated: dict[str, object]) -> tuple[int, str]:
    original = generated.get("original_multiple_choice", {})
    if not isinstance(original, dict):
        return 50, "No multiple-choice distractor provenance was available."
    options = original.get("options", [])
    correct_option_ids = set(_string_list(original.get("correct_option_ids", [])))
    distractors = [
        option
        for option in options
        if (
            isinstance(option, dict)
            and str(option.get("text", "")).strip()
            and str(option.get("option_id", "")) not in correct_option_ids
        )
    ]
    if len(distractors) >= 3:
        return 95, "Three plausible AWS distractors are present."
    if distractors:
        return 75, "Some AWS distractors are present."
    return 45, "Distractors are missing or empty."


def _technical_correctness_score(source_services: list[str], reference_answer: str, conflicts: list[str]) -> int:
    answer_tokens = _tokens(reference_answer)
    service_matches = any(_concept_present(service, answer_tokens) for service in source_services)
    if conflicts:
        return 55
    return 95 if service_matches else 70


def _source_safety_score(source: dict[str, object], question_text: str) -> tuple[int, str]:
    task_statement = str(source.get("task_statement", ""))
    source_type = str(source.get("source_type", ""))
    if source_type in {"official_sample", "official_practice_preview"}:
        return 90, "Official calibration row stores summarized metadata only."
    overlap = _overlap_ratio(_tokens(task_statement), _tokens(question_text))
    if overlap >= COPYING_TOKEN_LIMIT:
        return 60, "Generated wording is too close to the source task statement."
    return 98, "Generated wording is self-authored from public concept metadata."


def _overlap_ratio(source_tokens: set[str], generated_tokens: set[str]) -> float:
    if not source_tokens:
        return 0.0
    return len(source_tokens & generated_tokens) / len(source_tokens)


def _recommendation(total: int, conflicts: list[str], missing: list[str], source_safety_score: int) -> str:
    if conflicts or source_safety_score < 70 or total < 70:
        return "reject"
    if missing or total < 90:
        return "revise"
    return "accept"


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return []


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))
