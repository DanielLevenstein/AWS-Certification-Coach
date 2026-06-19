#!/usr/bin/env python3
"""Evaluate curated answers with the deterministic semantic_similarity model."""

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


CHART_FONT_SIZES = {
    "title": 20,
    "axis": 15,
    "tick": 16,
    "legend": 13,
    "annotation": 14,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument(
        "--evaluation-data",
        type=Path,
        action="append",
        default=None,
    )
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/semantic_similarity.json"))
    parser.add_argument("--chart-output", type=Path, default=Path("release/metrics/semantic_accuracy.png"))
    parser.add_argument("--training-metrics", type=Path, default=None)
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    metrics = evaluate_semantic_curated_answers(
        args.evaluation_data
        or [
            args.curated,
        ],
        questions,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    plot_semantic_accuracy(metrics, args.chart_output)
    print(json.dumps(metrics, indent=2))
    print(f"Semantic accuracy graph: {args.chart_output}")


def plot_semantic_accuracy(
    metrics: dict[str, object],
    output_path: Path,
) -> None:
    exact_letter_accuracy = float(metrics.get("semantic_exact_letter_accuracy", metrics["semantic_grade_accuracy"]))
    values = {
        "Semantic Accuracy": float(metrics["semantic_grade_accuracy"]) * 100,
        "Semantic Precision": float(metrics["semantic_precision"]) * 100,
        "Semantic Recall": float(metrics["semantic_recall"]) * 100,
        "Exact Letter Accuracy": exact_letter_accuracy * 100,
    }
    colors = ["#2ca02c", "#1f77b4", "#9467bd", "#ff7f0e"]
    figure, axis = plt.subplots(figsize=(10, 6))
    bars = axis.bar(values.keys(), values.values(), color=colors)
    axis.axhline(90, color="#d62728", linestyle="--", linewidth=2, label="Precision guardrail (90%)")
    axis.set_title("Semantic Diagnostic Accuracy", fontsize=CHART_FONT_SIZES["title"], pad=14)
    axis.set_ylabel("Percent", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_ylim(0, 100)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(fontsize=CHART_FONT_SIZES["legend"])
    axis.tick_params(axis="x", labelrotation=12, labelsize=CHART_FONT_SIZES["tick"])
    axis.tick_params(axis="y", labelsize=CHART_FONT_SIZES["tick"])
    for bar in bars:
        height = bar.get_height()
        axis.annotate(
            f"{height:.0f}%",
            (bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            fontsize=CHART_FONT_SIZES["annotation"],
        )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)

if __name__ == "__main__":
    main()
