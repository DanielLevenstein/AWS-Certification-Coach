#!/usr/bin/env python3
"""Generate curated negative answers that restate each question."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Protocol

from aws_certification_coach.config import current_schema_version


DEFAULT_MAX_REWORDING_ROWS = 20

class RewordingProvider(Protocol):
    def reword(self, question: dict[str, object]) -> str:
        """Return a natural-language restatement of the question, not an answer."""


class HeuristicRewordingProvider:
    """Offline provider for deterministic setup and tests."""

    def reword(self, question: dict[str, object]) -> str:
        prompt = str(question["question"]).strip().rstrip(".?")
        normalized_prompt = _without_leading_explain(prompt)
        return f"This question is asking the learner to identify and explain {normalized_prompt}."


class OpenAIRewordingProvider:
    """Question rewording provider backed by the OpenAI Responses API."""

    SYSTEM_PROMPT = (
        "You write wrong learner answers for AWS Certification Coach. "
        "Return only a natural-language restatement of the question. "
        "Do not name the correct AWS service, feature, or final answer unless it is already present in the question."
    )

    def __init__(self, model: str, temperature: float, max_output_tokens: int) -> None:
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

    def reword(self, question: dict[str, object]) -> str:
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Reword this question as a plausible but non-answer learner response. "
                        "It should sound natural and should not solve the question.\n\n"
                        f"Question:\n{question['question']}"
                    ),
                },
            ],
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
        )
        return response.output_text.strip()


def generate_rewording_rows(
    questions: list[dict[str, object]],
    provider: RewordingProvider,
    max_rows: int = DEFAULT_MAX_REWORDING_ROWS,
) -> list[dict[str, object]]:
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
        rows.append(_curated_row(question, provider.reword(question)))
        if len(rows) >= max_rows:
            break
    return rows


def _without_leading_explain(prompt: str) -> str:
    lowered = prompt.casefold()
    if lowered.startswith("explain "):
        return prompt[8:9].lower() + prompt[9:]
    return prompt[:1].lower() + prompt[1:]


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


def _curated_row(question: dict[str, object], reworded_answer: str) -> dict[str, object]:
    row = {
        "schema_version": current_schema_version("USER_FEEDBACK_VERSION"),
        "question": str(question["question"]),
        "exam_code": str(question.get("exam_code", "")),
        "reference_answer": str(question["reference_answer"]),
        "answer_given": reworded_answer.strip(),
        "correct_rating": "D",
        "rating_given": "A",
        "feedback_text": (
            "Generated question-restatement negative example: this answer rewords the prompt "
            "without identifying the correct AWS service, feature, or reasoning."
        ),
    }
    original = question.get("original_multiple_choice")
    if isinstance(original, dict):
        row["original_multiple_choice"] = original
    return row


def _provider(args: argparse.Namespace) -> RewordingProvider:
    if args.provider == "heuristic":
        return HeuristicRewordingProvider()
    return OpenAIRewordingProvider(
        model=args.model,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/curated_training_question_rewordings.json"))
    parser.add_argument("--provider", choices=["heuristic", "openai"], default="heuristic")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--max-output-tokens", type=int, default=120)
    parser.add_argument("--max-rows", type=int, default=DEFAULT_MAX_REWORDING_ROWS)
    args = parser.parse_args()

    questions = json.loads(args.questions.read_text(encoding="utf-8"))
    if not isinstance(questions, list):
        raise ValueError(f"Question artifact must be a JSON list: {args.questions}")
    rows = generate_rewording_rows(questions, _provider(args), max_rows=args.max_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(rows)} question-rewording curated examples into {args.output}.")


if __name__ == "__main__":
    main()
