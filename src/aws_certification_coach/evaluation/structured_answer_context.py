"""Question-matched few-shot context for OpenAI answer grading."""

from __future__ import annotations

import json
from pathlib import Path
import re

from aws_certification_coach.domain import Question
from aws_certification_coach.ratings import score_to_letter


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class StructuredAnswerContext:
    """Loads labeled answer examples and exposes only exact question matches."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._rows_by_question = self._load_rows()

    def for_question(self, question: Question) -> str:
        rows = self._rows_by_question.get(_normalized(question.question), [])
        if not rows:
            return ""
        examples = []
        for row in rows:
            for example in row.get("partial_answers", []):
                if not isinstance(example, dict):
                    continue
                rating = float(example.get("rating", 0.0))
                examples.append(
                    {
                        "answer": str(example.get("answer", "")),
                        "expected_score": round(rating * 100),
                        "expected_letter": score_to_letter(round(rating * 100)),
                    }
                )
        context = {
            "reference_answer": rows[0].get("reference_answer", question.reference_answer),
            "required_concepts": rows[0].get("required_concepts", question.required_concepts),
            "acceptable_answers": rows[0].get("acceptable_answers", question.acceptable_answers),
            "common_misconceptions": rows[0].get("common_misconceptions", question.common_misconceptions),
            "must_not_claim": rows[0].get("must_not_claim", question.must_not_claim),
            "graded_examples": examples,
        }
        return (
            "Structured grading evidence for this exact question:\n"
            + json.dumps(context, indent=2)
            + "\nUse these examples as rubric anchors, not as an exact-text requirement. "
            "Grade semantically equivalent answers consistently."
        )

    def examples_for_question(self, question: Question) -> list[tuple[str, int]]:
        """Return answer/score anchors for the exact question."""

        examples: list[tuple[str, int]] = []
        for row in self._rows_by_question.get(_normalized(question.question), []):
            for example in row.get("partial_answers", []):
                if not isinstance(example, dict) or not str(example.get("answer", "")).strip():
                    continue
                examples.append(
                    (
                        str(example["answer"]),
                        round(float(example.get("rating", 0.0)) * 100),
                    )
                )
        return examples

    def _load_rows(self) -> dict[str, list[dict[str, object]]]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        if not isinstance(payload, list):
            raise ValueError(f"Structured answer data must be a JSON list: {self.path}")
        rows_by_question: dict[str, list[dict[str, object]]] = {}
        for row in payload:
            if not isinstance(row, dict):
                continue
            question = _normalized(str(row.get("question", "")))
            if question:
                rows_by_question.setdefault(question, []).append(row)
        return rows_by_question


def _normalized(value: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(value.casefold()))
