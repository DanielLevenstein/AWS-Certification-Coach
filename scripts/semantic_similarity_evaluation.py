#!/usr/bin/env python3
"""Evaluate curated answers with deterministic semantic-aware scoring."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "release/metrics/.matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "release/metrics/.cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from aws_certification_coach.model_evaluation.semantic_similarity import (
    evaluate_semantic_curated_answers,
)
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/semantic_similarity.json"))
    parser.add_argument("--chart-output", type=Path, default=Path("release/metrics/semantic_accuracy.png"))
    parser.add_argument("--training-metrics", type=Path, default=None)
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    metrics = evaluate_semantic_curated_answers(args.curated, questions)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    training_metrics = args.training_metrics or args.output.parent / "training_metrics.json"
    plot_semantic_accuracy(metrics, args.chart_output, saved_model_accuracy=_saved_model_accuracy(training_metrics))
    print(json.dumps(metrics, indent=2))
    print(f"Semantic accuracy graph: {args.chart_output}")


def plot_semantic_accuracy(
    metrics: dict[str, object],
    output_path: Path,
    saved_model_accuracy: float | None = None,
) -> None:
    values = {
        "Semantic Accuracy": float(metrics["semantic_grade_accuracy"]) * 100,
        "Semantic Precision": float(metrics["semantic_precision"]) * 100,
        "Semantic Recall": float(metrics["semantic_recall"]) * 100,
    }
    colors = ["#2ca02c", "#1f77b4", "#9467bd"]
    if saved_model_accuracy is not None:
        values = {"Saved Model Accuracy": saved_model_accuracy * 100, **values}
        colors = ["#ff7f0e", *colors]
    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(values.keys(), values.values(), color=colors)
    axis.axhline(90, color="#d62728", linestyle="--", linewidth=2, label="Release target (90%)")
    axis.set_title("Semantic Diagnostic Accuracy")
    axis.set_ylabel("Percent")
    axis.set_ylim(0, 100)
    axis.grid(axis="y", alpha=0.25)
    axis.legend()
    axis.tick_params(axis="x", labelrotation=12)
    for bar in bars:
        height = bar.get_height()
        axis.annotate(
            f"{height:.0f}%",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
        )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def _saved_model_accuracy(training_metrics_path: Path) -> float | None:
    if not training_metrics_path.exists():
        return None
    training_metrics = json.loads(training_metrics_path.read_text(encoding="utf-8"))
    if not isinstance(training_metrics, dict):
        raise ValueError(f"Expected a JSON object: {training_metrics_path}")
    saved_model = training_metrics.get("saved_model", {})
    if isinstance(saved_model, dict) and "curated_grade_accuracy" in saved_model:
        return float(saved_model["curated_grade_accuracy"])
    return None


if __name__ == "__main__":
    main()
