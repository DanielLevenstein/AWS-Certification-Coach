"""JSON-backed storage for learner corrections to answer grades."""

from __future__ import annotations

import json
from pathlib import Path
import threading
from typing import Any

from aws_certification_coach.domain import MultipleChoiceQuestion, Question
from aws_certification_coach.ratings import letter_to_numeric


class UserFeedbackRepository:
    """Appends human-readable grade corrections to a local JSON artifact."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()

    def submit(
        self,
        question: Question,
        answer_given: str,
        rating_given: str,
        correct_rating: str,
    ) -> None:
        # Validate grades without writing derived numeric values to the artifact.
        letter_to_numeric(rating_given)
        letter_to_numeric(correct_rating)
        record = build_feedback_record(
            question=question,
            answer_given=answer_given,
            rating_given=rating_given,
            correct_rating=correct_rating,
        )
        with self._lock:
            rows = self._read()
            rows.append(record)
            self._write(rows)

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"User feedback must be a JSON list: {self.path}")
        return [row for row in rows if isinstance(row, dict)]

    def _write(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temporary_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        temporary_path.replace(self.path)


def build_feedback_record(
    question: Question,
    answer_given: str,
    rating_given: str,
    correct_rating: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "question_id": question.question_id,
        "question": question.question,
        "reference_answer": question.reference_answer,
        "original_multiple_choice": _multiple_choice_to_json(question.original_multiple_choice),
        "answer_given": answer_given,
        "correct_rating": correct_rating,
        "rating_given": rating_given,
    }


def _multiple_choice_to_json(original: MultipleChoiceQuestion | None) -> dict[str, Any] | None:
    if original is None:
        return None
    return {
        "question": original.question,
        "options": [
            {"option_id": option.option_id, "text": option.text}
            for option in original.options
        ],
        "correct_option_ids": list(original.correct_option_ids),
        "explanation": original.explanation,
        "source_name": original.source_name,
        "source_url": original.source_url,
        "source_license_notes": original.source_license_notes,
    }
