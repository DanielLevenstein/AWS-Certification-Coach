"""Feature extraction for answer classification."""

from __future__ import annotations

import re

from aws_certification_coach.domain import Question


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class AnswerFeatureExtractor:
    """Extracts stable lexical and provenance features for a question answer."""

    feature_names = [
        "bias",
        "reference_jaccard",
        "reference_answer_containment",
        "answer_reference_containment",
        "correct_option_exact",
        "correct_option_jaccard",
        "correct_option_answer_containment",
        "incorrect_option_jaccard",
        "incorrect_option_answer_containment",
        "explanation_exact",
        "explanation_jaccard",
        "answer_length_ratio",
    ]

    def extract(self, question: Question, answer: str) -> list[float]:
        answer_tokens = _tokens(answer)
        reference_tokens = _tokens(question.reference_answer)
        correct_option_texts, incorrect_option_texts = _option_texts(question)
        correct_jaccard = max((_jaccard(answer_tokens, _tokens(text)) for text in correct_option_texts), default=0.0)
        incorrect_jaccard = max((_jaccard(answer_tokens, _tokens(text)) for text in incorrect_option_texts), default=0.0)
        correct_containment = max((_containment(_tokens(text), answer_tokens) for text in correct_option_texts), default=0.0)
        incorrect_containment = max((_containment(_tokens(text), answer_tokens) for text in incorrect_option_texts), default=0.0)
        explanation = question.original_multiple_choice.explanation if question.original_multiple_choice else ""
        explanation_tokens = _tokens(explanation)
        return [
            1.0,
            _jaccard(answer_tokens, reference_tokens),
            _containment(reference_tokens, answer_tokens),
            _containment(answer_tokens, reference_tokens),
            1.0 if _normalized(answer) in {_normalized(text) for text in correct_option_texts} else 0.0,
            correct_jaccard,
            correct_containment,
            incorrect_jaccard,
            incorrect_containment,
            1.0 if explanation and _normalized(answer) == _normalized(explanation) else 0.0,
            _jaccard(answer_tokens, explanation_tokens),
            min(2.0, len(answer_tokens) / max(1, len(reference_tokens))),
        ]


def _option_texts(question: Question) -> tuple[list[str], list[str]]:
    original = question.original_multiple_choice
    if original is None:
        return [], []
    correct_ids = set(original.correct_option_ids)
    correct = [option.text for option in original.options if option.option_id in correct_ids]
    incorrect = [option.text for option in original.options if option.option_id not in correct_ids]
    return correct, incorrect


def _tokens(value: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(value.casefold()))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _containment(required: set[str], candidate: set[str]) -> float:
    if not required:
        return 0.0
    return len(required & candidate) / len(required)


def _normalized(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.casefold()))
