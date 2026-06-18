#!/usr/bin/env python3
"""Evaluate generated Developer Associate questions for source fidelity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.question_fidelity.model import evaluate_question_batch


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("data/original_questions/developer_associate_sources.json"))
    parser.add_argument("--generated", type=Path, default=Path("data/generated/developer_question_expansion.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/question_fidelity.json"))
    args = parser.parse_args()

    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    generated = json.loads(args.generated.read_text(encoding="utf-8"))
    metrics = evaluate_question_batch(sources, generated)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
