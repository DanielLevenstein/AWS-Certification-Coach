#!/usr/bin/env python3
"""Generate A-grade curated examples with full-sentence explanations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.config import current_schema_version


DEFAULT_MAX_ROWS = 80


def generate_full_sentence_rows(questions: list[dict[str, object]], max_rows: int = DEFAULT_MAX_ROWS) -> list[dict[str, object]]:
    if max_rows < 1:
        raise ValueError("max_rows must be at least 1.")
    rows = []
    seen_questions: set[tuple[str, str]] = set()
    for question in questions:
        _validate_question_row(question)
        question_key = _question_dedupe_key(question)
        if question_key in seen_questions:
            continue
        seen_questions.add(question_key)
        rows.append(_curated_row(question, _full_sentence_answer(question)))
        if len(rows) >= max_rows:
            break
    return rows


def _validate_question_row(question: object) -> None:
    if not isinstance(question, dict):
        raise ValueError("Question rows must be JSON objects.")
    for field in ("question", "reference_answer"):
        if not str(question.get(field, "")).strip():
            raise ValueError(f"Question row is missing {field}.")


def _question_dedupe_key(question: dict[str, object]) -> tuple[str, str]:
    return (
        _normalized_text(question.get("question", "")),
        _normalized_text(question.get("reference_answer", "")),
    )


def _normalized_text(value: object) -> str:
    return " ".join(str(value).casefold().split())


def _full_sentence_answer(question: dict[str, object]) -> str:
    reference = str(question["reference_answer"]).strip().rstrip(".")
    if reference.casefold().startswith("use "):
        answer = f"The best answer is to use {reference[4:]}."
    else:
        answer = f"{reference}."
    concepts = [
        str(concept).strip()
        for concept in question.get("key_concepts", [])
        if str(concept).strip()
    ]
    if len(concepts) >= 2:
        answer = f"{answer} This addresses {concepts[0]} and {concepts[1]}."
    return answer


def _curated_row(question: dict[str, object], answer: str) -> dict[str, object]:
    row = {
        "schema_version": current_schema_version("USER_FEEDBACK_VERSION"),
        "question": str(question["question"]),
        "exam_code": str(question.get("exam_code", "")),
        "reference_answer": str(question["reference_answer"]),
        "answer_given": answer,
        "correct_rating": "A",
        "rating_given": "C",
        "feedback_text": (
            "Generated full-sentence positive example: this answer names the correct AWS service "
            "or feature and explains the relevant scenario concept."
        ),
    }
    original = question.get("original_multiple_choice")
    if isinstance(original, dict):
        row["original_multiple_choice"] = original
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/curated_training_full_sentence_answers.json"))
    parser.add_argument("--max-rows", type=int, default=DEFAULT_MAX_ROWS)
    args = parser.parse_args()

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    if not isinstance(questions, list):
        raise ValueError(f"Question artifact must be a JSON list: {args.questions}")
    rows = generate_full_sentence_rows(questions, max_rows=args.max_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(rows)} full-sentence curated examples into {args.output}.")


if __name__ == "__main__":
    main()
