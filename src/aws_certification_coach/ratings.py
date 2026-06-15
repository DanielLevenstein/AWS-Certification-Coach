"""Shared letter-grade conversion for display, feedback, and training."""

from __future__ import annotations


LETTER_RATINGS = ("A", "B", "C", "D", "F")
LETTER_RATING_VALUES = {
    "A": 0.95,
    "B": 0.85,
    "C": 0.75,
    "D": 0.65,
    "F": 0.25,
}
GRADE_BANDS = {
    "A": "A/B",
    "B": "A/B",
    "C": "C/D",
    "D": "C/D",
    "F": "F",
}


def score_to_letter(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def letter_to_grade_band(rating: object) -> str:
    normalized = str(rating).strip().upper()
    try:
        return GRADE_BANDS[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported rating {rating!r}; expected one of {', '.join(LETTER_RATINGS)}.") from exc


def letter_to_numeric(rating: object) -> float:
    normalized = str(rating).strip().upper()
    try:
        return LETTER_RATING_VALUES[normalized]
    except KeyError as exc:
        raise ValueError(f"Unsupported rating {rating!r}; expected one of {', '.join(LETTER_RATINGS)}.") from exc


def letter_to_binary_label(rating: object) -> int:
    return 1 if letter_to_numeric(rating) >= 0.70 else 0
