#!/usr/bin/env python3
"""Run model-quality gates independently from unit tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.model_evaluation.suite import run_model_evaluation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("data/generated/questions_with_answers_training.json"))
    parser.add_argument("--app-questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--training-data", type=Path, default=Path("data/generated/questions_with_answers_training.json"))
    parser.add_argument("--curated-data", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/model_evaluation.json"))
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--min-semantic-precision", type=float, default=0.80)
    args = parser.parse_args()

    report = run_model_evaluation(
        args.questions,
        args.app_questions,
        args.training_data,
        args.curated_data,
        epochs=args.epochs,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    semantic = report["semantic_similarity"]
    failures = []
    if semantic["semantic_precision"] < args.min_semantic_precision:
        failures.append(
            f"semantic precision {semantic['semantic_precision']:.2%} is below {args.min_semantic_precision:.2%}"
        )
    if failures:
        raise SystemExit("Model evaluation failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
