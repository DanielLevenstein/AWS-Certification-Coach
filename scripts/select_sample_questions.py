"""Select a random app-facing question sample from a training artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/generated/questions_with_answers_generated.json")
    parser.add_argument("--output", default="data/questions/sample_questions.json")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Input question artifact must be a JSON list.")
    if len(rows) < args.count:
        raise ValueError(f"Cannot sample {args.count} questions from only {len(rows)} rows.")

    sampler = random.Random(args.seed) if args.seed is not None else random
    sample = [_app_question_row(row) for row in sampler.sample(rows, args.count)]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sample, indent=2) + "\n", encoding="utf-8")
    print(f"Selected {len(sample)} questions from {args.input} into {args.output}.")


def _app_question_row(row: object) -> dict:
    if not isinstance(row, dict):
        raise ValueError("Question rows must be JSON objects.")
    allowed_fields = {
        "question_id",
        "certification",
        "domain",
        "difficulty",
        "question",
        "reference_answer",
        "key_concepts",
        "original_multiple_choice",
    }
    return {
        key: value
        for key, value in row.items()
        if key in allowed_fields
    }


if __name__ == "__main__":
    main()
