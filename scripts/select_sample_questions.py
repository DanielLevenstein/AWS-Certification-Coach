"""Select a random sample of training questions for the app."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/questions/transformed_freeform_generated.json")
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
    sample = sampler.sample(rows, args.count)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(sample, indent=2) + "\n", encoding="utf-8")
    print(f"Selected {len(sample)} questions from {args.input} into {args.output}.")


if __name__ == "__main__":
    main()
