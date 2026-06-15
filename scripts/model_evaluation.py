#!/usr/bin/env python3
"""Run model-quality gates independently from unit tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.model_evaluation import run_model_evaluation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=Path("data/generated/questions_with_answers_generated.json"))
    parser.add_argument("--app-questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--training-data", type=Path, default=Path("data/generated/questions_with_answers_generated.json"))
    parser.add_argument("--curated-data", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/model_evaluation.json"))
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--max-mse", type=float, default=0.06)
    parser.add_argument("--min-rubric-accuracy", type=float, default=0.90)
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

    held_out = report["held_out_performance"]
    rubric = report["rubric_adherence"]
    failures = []
    if held_out["mse"] > args.max_mse:
        failures.append(f"held-out MSE {held_out['mse']:.4f} exceeds {args.max_mse:.4f}")
    if rubric["grade_accuracy"] < args.min_rubric_accuracy:
        failures.append(
            f"curated grade-band accuracy {rubric['grade_accuracy']:.2%} is below {args.min_rubric_accuracy:.2%}"
        )
    if failures:
        raise SystemExit("Model evaluation failed: " + "; ".join(failures))


if __name__ == "__main__":
    main()
