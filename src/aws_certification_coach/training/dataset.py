"""Dataset loading for answer classification training."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class AnswerClassificationExample:
    question_id: str
    answer: str
    label: int
    source: str = ""


def load_answer_classification_examples(path: str | Path) -> list[AnswerClassificationExample]:
    with Path(path).open("r", encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"Training data must be a JSON list: {path}")
    return [_example_from_json(row) for row in rows]


def _example_from_json(row: object) -> AnswerClassificationExample:
    if not isinstance(row, dict):
        raise ValueError("Training examples must be JSON objects.")
    return AnswerClassificationExample(
        question_id=str(row["question_id"]),
        answer=str(row["answer"]),
        label=int(row["label"]),
        source=str(row.get("source", "")),
    )
