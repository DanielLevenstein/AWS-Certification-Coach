"""JSON-backed storage for learner corrections to answer grades."""

from __future__ import annotations

import json
from pathlib import Path
import re
import threading
from typing import Any

from aws_certification_coach.domain import MultipleChoiceQuestion, Question
from aws_certification_coach.ratings import letter_to_numeric


class UserFeedbackRepository:
    """Appends human-readable grade corrections to a local JSON artifact."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.schema_version = _schema_version_from_path(self.path)

    def submit(
        self,
        question: Question,
        answer_given: str,
        rating_given: str,
        correct_rating: str,
        feedback_text: str = "",
    ) -> None:
        # Validate grades without writing derived numeric values to the artifact.
        letter_to_numeric(rating_given)
        letter_to_numeric(correct_rating)
        record = build_feedback_record(
            question=question,
            answer_given=answer_given,
            rating_given=rating_given,
            correct_rating=correct_rating,
            feedback_text=feedback_text,
            schema_version=self.schema_version,
        )
        with self._lock:
            rows = self._read()
            rows.append(record)
            self._write(rows)

    def export_json(self) -> str:
        """Return the stored feedback artifact as formatted JSON."""
        with self._lock:
            rows = self._read()
        return json.dumps(rows, indent=2) + "\n"

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
    feedback_text: str = "",
    schema_version: int | float = 1,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "question": question.question,
        "exam_code": question.exam_code,
        "reference_answer": question.reference_answer,
        "original_multiple_choice": _multiple_choice_to_json(question.original_multiple_choice),
        "answer_given": answer_given,
        "correct_rating": correct_rating,
        "rating_given": rating_given,
        "feedback_text": feedback_text.strip(),
    }


def _schema_version_from_path(path: Path) -> int | float:
    name = path.name
    match = re.search(r"\.v(\d+(?:\.\d+)?)\.", name)
    if match:
        version = match.group(1)
        return float(version) if "." in version else int(version)
    if name.startswith("generated_feedback"):
        return 0
    return 1


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
