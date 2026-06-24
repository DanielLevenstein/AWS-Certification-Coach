"""Feature extraction for answer classification."""

from __future__ import annotations

import re

from aws_certification_coach.domain import Question
from aws_certification_coach.knowledge_base import KnowledgeBase, load_knowledge_base


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
GENERIC_TOKENS = {"amazon", "aws", "classes", "data", "feature", "service", "the", "use"}
AMBIGUOUS_TOKENS = {"route", "s3"}


class AnswerFeatureExtractor:
    """Extracts stable lexical and provenance features for a question answer."""

    feature_names = [
        "bias",
        "reference_jaccard",
        "reference_answer_containment",
        "answer_reference_containment",
        "short_answer_jaccard",
        "short_answer_containment",
        "answer_short_answer_containment",
        "short_answer_length_ratio",
        "correct_option_exact",
        "correct_option_jaccard",
        "correct_option_answer_containment",
        "incorrect_option_jaccard",
        "incorrect_option_answer_containment",
        "explanation_exact",
        "explanation_jaccard",
        "answer_length_ratio",
        "correct_distinctive_token_coverage",
        "has_correct_distinctive_token",
        "incorrect_distinctive_token_coverage",
        "acceptable_answer_exact",
        "acceptable_answer_jaccard",
        "acceptable_answer_containment",
        "answer_acceptable_answer_containment",
        "required_concept_coverage",
        "common_misconception_coverage",
        "must_not_claim_coverage",
        "distractor_margin",
    ]

    def __init__(
        self,
        answer_form: str = "long",
        knowledge_base: KnowledgeBase | None = None,
    ) -> None:
        if answer_form not in {"long", "short", "both"}:
            raise ValueError("answer_form must be one of: long, short, both")
        self.answer_form = answer_form
        self.knowledge_base = knowledge_base or load_knowledge_base()

    def extract(self, question: Question, answer: str) -> list[float]:
        answer_tokens = _tokens(answer, self.knowledge_base)
        reference_tokens = _tokens(question.reference_answer, self.knowledge_base)
        short_answer_tokens = _tokens(correct_answer_text(question), self.knowledge_base)
        correct_option_texts, incorrect_option_texts = _option_texts(question)
        correct_answers = [correct_answer_text(question)]
        correct_distinctive_tokens = _distinctive_tokens(correct_answer_text(question), self.knowledge_base)
        use_long = self.answer_form in {"long", "both"}
        use_short = self.answer_form in {"short", "both"}
        correct_jaccard = max(
            (_jaccard(answer_tokens, _tokens(text, self.knowledge_base)) for text in correct_option_texts),
            default=0.0,
        )
        incorrect_jaccard = max(
            (_jaccard(answer_tokens, _tokens(text, self.knowledge_base)) for text in incorrect_option_texts),
            default=0.0,
        )
        correct_containment = max(
            (_containment(_tokens(text, self.knowledge_base), answer_tokens) for text in correct_option_texts),
            default=0.0,
        )
        incorrect_containment = max(
            (_containment(_tokens(text, self.knowledge_base), answer_tokens) for text in incorrect_option_texts),
            default=0.0,
        )
        incorrect_distinctive_coverage = max(
            (
                _containment(_distinctive_tokens(text, self.knowledge_base), answer_tokens)
                for text in incorrect_option_texts
            ),
            default=0.0,
        )
        explanation = question.original_multiple_choice.explanation if question.original_multiple_choice else ""
        explanation_tokens = _tokens(explanation, self.knowledge_base)
        acceptable_answer_tokens = [_tokens(text, self.knowledge_base) for text in question.acceptable_answers]
        acceptable_answer_exact = any(
            _normalized_answer(answer, self.knowledge_base) == _normalized_answer(text, self.knowledge_base)
            for text in question.acceptable_answers
        )
        required_concepts = question.required_concepts or question.key_concepts
        return [
            1.0,
            _jaccard(answer_tokens, reference_tokens) if use_long else 0.0,
            _containment(reference_tokens, answer_tokens) if use_long else 0.0,
            _containment(answer_tokens, reference_tokens) if use_long else 0.0,
            _jaccard(answer_tokens, short_answer_tokens) if use_short else 0.0,
            _containment(short_answer_tokens, answer_tokens) if use_short else 0.0,
            _containment(answer_tokens, short_answer_tokens) if use_short else 0.0,
            min(2.0, len(answer_tokens) / max(1, len(short_answer_tokens))) if use_short else 0.0,
            1.0
            if use_short
            and _normalized_answer(answer, self.knowledge_base)
            in {_normalized_answer(text, self.knowledge_base) for text in correct_answers}
            else 0.0,
            correct_jaccard,
            correct_containment,
            incorrect_jaccard,
            incorrect_containment,
            1.0
            if explanation
            and _normalized(answer, self.knowledge_base) == _normalized(explanation, self.knowledge_base)
            else 0.0,
            _jaccard(answer_tokens, explanation_tokens),
            min(2.0, len(answer_tokens) / max(1, len(reference_tokens))),
            _containment(correct_distinctive_tokens, answer_tokens) if use_short else 0.0,
            1.0 if use_short and correct_distinctive_tokens & answer_tokens else 0.0,
            incorrect_distinctive_coverage,
            1.0 if acceptable_answer_exact else 0.0,
            max((_jaccard(answer_tokens, tokens) for tokens in acceptable_answer_tokens), default=0.0),
            max((_containment(tokens, answer_tokens) for tokens in acceptable_answer_tokens), default=0.0),
            max((_containment(answer_tokens, tokens) for tokens in acceptable_answer_tokens), default=0.0),
            _concept_list_coverage(required_concepts, answer_tokens, self.knowledge_base),
            _concept_list_coverage(question.common_misconceptions, answer_tokens, self.knowledge_base),
            _concept_list_coverage(question.must_not_claim, answer_tokens, self.knowledge_base),
            max(0.0, correct_containment - incorrect_containment),
        ]


def _option_texts(question: Question) -> tuple[list[str], list[str]]:
    original = question.original_multiple_choice
    if original is None:
        return [], []
    correct_ids = set(original.correct_option_ids)
    correct = [option.text for option in original.options if option.option_id in correct_ids]
    incorrect = [option.text for option in original.options if option.option_id not in correct_ids]
    return correct, incorrect


def correct_answer_text(question: Question) -> str:
    """Return the concise correct answer text used for model training."""

    original = question.original_multiple_choice
    if original is None:
        return _clean_answer_text(question.reference_answer)
    correct_ids = set(original.correct_option_ids)
    correct_options = [
        _clean_answer_text(option.text)
        for option in original.options
        if option.option_id in correct_ids
    ]
    return "; ".join(option for option in correct_options if option) or _clean_answer_text(question.reference_answer)


def _tokens(value: str, knowledge_base: KnowledgeBase) -> set[str]:
    return set(TOKEN_PATTERN.findall(knowledge_base.canonicalize(value)))


def _distinctive_tokens(value: str, knowledge_base: KnowledgeBase) -> set[str]:
    return _tokens(value, knowledge_base) - GENERIC_TOKENS - AMBIGUOUS_TOKENS


def _concept_list_coverage(
    concepts: list[str],
    answer_tokens: set[str],
    knowledge_base: KnowledgeBase,
) -> float:
    if not concepts:
        return 0.0
    covered = 0
    for concept in concepts:
        term_coverages = [
            _containment(_distinctive_tokens(term, knowledge_base), answer_tokens)
            for term in knowledge_base.terms_for_concept(concept)
            if _distinctive_tokens(term, knowledge_base)
        ]
        if term_coverages and max(term_coverages) >= 0.5:
            covered += 1
    return covered / len(concepts)


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _containment(required: set[str], candidate: set[str]) -> float:
    if not required:
        return 0.0
    return len(required & candidate) / len(required)


def _normalized(value: str, knowledge_base: KnowledgeBase) -> str:
    return knowledge_base.canonicalize(value)


def _normalized_answer(value: str, knowledge_base: KnowledgeBase) -> str:
    return _normalized(_clean_answer_text(value), knowledge_base)


def _clean_answer_text(value: str) -> str:
    cleaned = re.sub(r"^\s*[A-Z]\s*[\).:-]\s*", "", value.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"^use\s+", "", cleaned, flags=re.IGNORECASE)
    return cleaned.rstrip(".").strip()
