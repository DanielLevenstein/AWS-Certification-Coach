"""Build service-comparison freeform questions from MCQ source rows."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class ComparisonCandidate:
    """A source MCQ option pair suitable for comparison-question generation."""

    source: dict[str, object]
    best_choice: str
    near_miss_choice: str
    overlap_score: int


class ServiceComparisonQuestionService:
    """Draft transformer for v2.2 service-comparison freeform questions."""

    def build_questions(self, source_rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
        questions = []
        for source in source_rows:
            candidate = self.find_candidate(source)
            if candidate is not None:
                questions.append(self.build_question(candidate))
        return questions

    def find_candidate(self, source: dict[str, object]) -> ComparisonCandidate | None:
        original = _original_multiple_choice(source)
        correct_ids = set(str(option_id) for option_id in original.get("correct_option_ids", []))
        options = [option for option in original.get("options", []) if isinstance(option, dict)]
        if len(correct_ids) != 1 or len(options) < 2:
            return None

        best_options = [
            _option_text(option)
            for option in options
            if str(option.get("option_id", "")) in correct_ids
        ]
        if len(best_options) != 1:
            return None
        best_choice = best_options[0]
        distractors = [
            _option_text(option)
            for option in options
            if str(option.get("option_id", "")) not in correct_ids
        ]
        scored = [
            (_near_miss_score(source, best_choice, distractor), distractor)
            for distractor in distractors
            if _looks_like_service_choice(distractor)
        ]
        if not scored:
            return None
        overlap_score, near_miss_choice = max(scored, key=lambda item: (item[0], len(item[1])))
        if overlap_score < 1:
            return None
        return ComparisonCandidate(
            source=source,
            best_choice=best_choice,
            near_miss_choice=near_miss_choice,
            overlap_score=overlap_score,
        )

    def build_question(self, candidate: ComparisonCandidate) -> dict[str, object]:
        source = candidate.source
        concepts = [str(concept) for concept in source.get("key_concepts", []) if str(concept).strip()]
        if not concepts:
            concepts = _concepts_from_text(candidate.best_choice, candidate.near_miss_choice)

        scenario = _source_question(source)
        comparison_prompt = (
            f"Compare {candidate.best_choice} with {candidate.near_miss_choice} for this scenario. "
            f"Explain why {candidate.best_choice} is the better fit, why "
            f"{candidate.near_miss_choice} is tempting but weaker, and which scenario constraints drive the decision. "
            f"Scenario: {scenario}"
        )
        reference_answer = _comparison_reference_answer(source, candidate)
        rubric_metadata = _rubric_metadata(concepts, candidate, reference_answer)
        return {
            "certification": source.get("certification", ""),
            "exam_code": source.get("exam_code", ""),
            "domain": source.get("domain", ""),
            "difficulty": source.get("difficulty", ""),
            "question_type": "service_comparison",
            "question": comparison_prompt,
            "reference_answer": reference_answer,
            "key_concepts": concepts,
            **rubric_metadata,
            "compared_services": [candidate.best_choice, candidate.near_miss_choice],
            "best_choice": candidate.best_choice,
            "near_miss_choice": candidate.near_miss_choice,
            "tradeoff_concepts": _tradeoff_concepts(concepts, scenario),
            "comparison_rationale": _comparison_rationale(source, candidate),
            "original_multiple_choice": _original_multiple_choice(source),
        }


def _original_multiple_choice(source: dict[str, object]) -> dict[str, object]:
    original = source.get("original_multiple_choice", {})
    return original if isinstance(original, dict) else {}


def _source_question(source: dict[str, object]) -> str:
    original = _original_multiple_choice(source)
    return str(original.get("question") or source.get("question") or "").strip()


def _option_text(option: dict[str, object]) -> str:
    return str(option.get("text", "")).strip()


def _looks_like_service_choice(text: str) -> bool:
    normalized = text.lower()
    if not normalized:
        return False
    weak_phrases = ["alarm only", "dashboard", "manual", "local cron", "increase memory without"]
    if any(phrase in normalized for phrase in weak_phrases):
        return False
    return bool(re.search(r"\b(aws|amazon|s3|sqs|sns|rds|dynamodb|lambda|api gateway|eventbridge|cloudwatch)\b", normalized))


def _near_miss_score(source: dict[str, object], best_choice: str, distractor: str) -> int:
    source_tokens = set(_normalized_tokens(" ".join(str(concept) for concept in source.get("key_concepts", []))))
    source_tokens.update(_normalized_tokens(_source_question(source)))
    best_tokens = set(_normalized_tokens(best_choice))
    distractor_tokens = set(_normalized_tokens(distractor))
    return len(distractor_tokens & (source_tokens | best_tokens))


def _tokens(text: str) -> list[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "as",
        "for",
        "in",
        "of",
        "or",
        "the",
        "to",
        "use",
        "with",
    }
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 1 and token not in stop_words
    ]


def _normalized_tokens(text: str) -> list[str]:
    tokens = []
    for token in _tokens(text):
        tokens.append(token[:6] if len(token) > 6 else token)
    return tokens


def _concepts_from_text(*values: str) -> list[str]:
    concepts = []
    for value in values:
        cleaned = re.sub(r"^(use|configure|create|adjust|add)\s+", "", value.strip(), flags=re.IGNORECASE)
        if cleaned and cleaned not in concepts:
            concepts.append(cleaned)
    return concepts


def _comparison_reference_answer(source: dict[str, object], candidate: ComparisonCandidate) -> str:
    explanation = str(_original_multiple_choice(source).get("explanation") or source.get("reference_answer") or "").strip()
    if not explanation:
        explanation = f"{candidate.best_choice} is the better fit for the stated scenario constraints."
    return (
        f"{explanation} {candidate.near_miss_choice} is a plausible alternative, but it does not match the "
        "decisive scenario constraint as directly. A strong answer should name both options, explain the "
        "service boundary, and connect the tradeoff to the scenario."
    )


def _tradeoff_concepts(concepts: list[str], scenario: str) -> list[str]:
    tradeoffs = []
    for concept in concepts:
        lowered = concept.lower()
        if any(keyword in lowered for keyword in ["latency", "replication", "failover", "fanout", "retry", "cost"]):
            tradeoffs.append(concept)
    if not tradeoffs:
        scenario_tokens = set(_tokens(scenario))
        for label, keywords in {
            "operational overhead": {"managed", "automatic", "serverless"},
            "resilience": {"failover", "durability", "available", "recovery"},
            "integration semantics": {"event", "queue", "message", "workflow"},
        }.items():
            if scenario_tokens & keywords:
                tradeoffs.append(label)
    return tradeoffs or concepts[:3]


def _comparison_rationale(source: dict[str, object], candidate: ComparisonCandidate) -> str:
    domain = str(source.get("domain", "the target domain")).strip() or "the target domain"
    return (
        f"Compare the correct {domain} decision against the strongest plausible distractor. "
        f"The expected answer should explain why {candidate.best_choice} satisfies the scenario more directly "
        f"than {candidate.near_miss_choice}."
    )


def _rubric_metadata(
    concepts: list[str],
    candidate: ComparisonCandidate,
    reference_answer: str,
) -> dict[str, list[str]]:
    return {
        "required_concepts": concepts,
        "bonus_concepts": ["service boundary", "scenario constraint tradeoff"],
        "common_misconceptions": [
            f"{candidate.near_miss_choice} satisfies the scenario as directly as {candidate.best_choice}."
        ],
        "acceptable_answers": [candidate.best_choice, reference_answer],
        "must_not_claim": [f"{candidate.near_miss_choice} is the better fit than {candidate.best_choice}."],
    }
