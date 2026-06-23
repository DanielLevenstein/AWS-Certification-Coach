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
    parser.add_argument("--per-grade-output", type=Path, default=None)
    parser.add_argument("--grade-band-output", type=Path, default=None)
    parser.add_argument("--letter-distance-output", type=Path, default=None)
    parser.add_argument("--answer-model-evaluation", type=Path, default=None)
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
    answer_model_evaluation = (
        json.loads(args.answer_model_evaluation.read_text(encoding="utf-8"))
        if args.answer_model_evaluation is not None
        else None
    )
    plot_semantic_accuracy(metrics, args.chart_output, answer_model_evaluation)
    if args.per_grade_output is not None:
        plot_per_grade_metrics(answer_model_evaluation or {}, args.per_grade_output)
    if args.grade_band_output is not None:
        plot_grade_band_metrics(answer_model_evaluation or {}, args.grade_band_output)
    if args.letter_distance_output is not None:
        plot_letter_distance_metrics(answer_model_evaluation or {}, args.letter_distance_output)
    print(json.dumps(metrics, indent=2))
    print(f"Semantic accuracy graph: {args.chart_output}")


def plot_semantic_accuracy(
    metrics: dict[str, object],
    output_path: Path,
    answer_model_evaluation: dict[str, object] | None = None,
) -> None:
    exact_letter_accuracy = float(metrics.get("semantic_exact_letter_accuracy", metrics["semantic_grade_accuracy"]))
    values = {
        "Semantic Accuracy": float(metrics["semantic_grade_accuracy"]) * 100,
        "Semantic Precision": float(metrics["semantic_precision"]) * 100,
        "Semantic Recall": float(metrics["semantic_recall"]) * 100,
        "Exact Letter Accuracy": exact_letter_accuracy * 100,
    }
    splits = (answer_model_evaluation or {}).get("splits", {})
    test_split = splits.get("test") if isinstance(splits, dict) else None
    if isinstance(test_split, dict) and "within_one_letter_accuracy" in test_split:
        values["Within 1 Letter"] = float(test_split["within_one_letter_accuracy"]) * 100
    colors = ["#2ca02c", "#1f77b4", "#9467bd", "#ff7f0e", "#17becf"]
    figure, axis = plt.subplots(figsize=(12, 6))
    bars = axis.bar(values.keys(), values.values(), color=colors)
    axis.axhline(90, color="#d62728", linestyle="--", linewidth=2, label="Precision guardrail (90%)")
    axis.set_title("Semantic Diagnostic Accuracy", fontsize=CHART_FONT_SIZES["title"], pad=14)
    axis.set_ylabel("Percent", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_ylim(0, 108)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="lower left", fontsize=CHART_FONT_SIZES["legend"])
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


def plot_per_grade_metrics(answer_model_evaluation: dict[str, object], output_path: Path) -> None:
    """Render final-test precision and recall for each grade."""

    splits = answer_model_evaluation.get("splits", {})
    test_split = splits.get("test", {}) if isinstance(splits, dict) else {}
    per_grade = test_split.get("per_grade", {}) if isinstance(test_split, dict) else {}
    if not isinstance(per_grade, dict):
        raise ValueError("Answer model evaluation does not define per_grade metrics.")

    grades = ("A", "B", "C", "D", "F")
    precisions = []
    recalls = []
    precision_labels = []
    recall_labels = []
    for grade in grades:
        metrics = per_grade.get(grade, {})
        precision = metrics.get("precision") if isinstance(metrics, dict) else None
        recall = metrics.get("recall") if isinstance(metrics, dict) else None
        precisions.append(0.0 if precision is None else float(precision) * 100)
        recalls.append(0.0 if recall is None else float(recall) * 100)
        precision_labels.append("N/A" if precision is None else f"{float(precision):.0%}")
        recall_labels.append("N/A" if recall is None else f"{float(recall):.0%}")

    figure, axis = plt.subplots(figsize=(8, 5))
    positions = list(range(len(grades)))
    width = 0.36
    precision_bars = axis.bar(
        [position - width / 2 for position in positions],
        precisions,
        width,
        color=["#276749", "#2b6cb0", "#6b46c1", "#c05621", "#9b2c2c"],
        label="Precision",
    )
    recall_bars = axis.bar(
        [position + width / 2 for position in positions],
        recalls,
        width,
        color=["#68d391", "#90cdf4", "#b794f4", "#fbd38d", "#feb2b2"],
        label="Recall",
    )
    axis.set_ylim(0, 108)
    axis.set_xticks(positions, grades)
    axis.set_ylabel("Percent", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_xlabel("Grade", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_title("Per-Grade Precision and Recall", fontsize=CHART_FONT_SIZES["title"], pad=14)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="lower right", fontsize=CHART_FONT_SIZES["legend"])
    axis.bar_label(
        precision_bars,
        labels=precision_labels,
        padding=3,
        fontsize=CHART_FONT_SIZES["annotation"] - 2,
    )
    axis.bar_label(
        recall_bars,
        labels=recall_labels,
        padding=3,
        fontsize=CHART_FONT_SIZES["annotation"] - 2,
    )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def plot_grade_band_metrics(answer_model_evaluation: dict[str, object], output_path: Path) -> None:
    """Render precision and recall for the A, BC, and DF reporting bands."""

    splits = answer_model_evaluation.get("splits", {})
    test_split = splits.get("test", {}) if isinstance(splits, dict) else {}
    per_band = test_split.get("per_grade_band", {}) if isinstance(test_split, dict) else {}
    if not isinstance(per_band, dict):
        raise ValueError("Answer model evaluation does not define per_grade_band metrics.")

    bands = ("A", "BC", "DF")
    precisions, recalls = [], []
    precision_labels, recall_labels = [], []
    for band in bands:
        metrics = per_band.get(band, {})
        precision = metrics.get("precision") if isinstance(metrics, dict) else None
        recall = metrics.get("recall") if isinstance(metrics, dict) else None
        precisions.append(0.0 if precision is None else float(precision) * 100)
        recalls.append(0.0 if recall is None else float(recall) * 100)
        precision_labels.append("N/A" if precision is None else f"{float(precision):.0%}")
        recall_labels.append("N/A" if recall is None else f"{float(recall):.0%}")

    figure, axis = plt.subplots(figsize=(8, 5))
    positions = list(range(len(bands)))
    width = 0.36
    precision_bars = axis.bar(
        [position - width / 2 for position in positions],
        precisions,
        width,
        color=["#276749", "#6b46c1", "#9b2c2c"],
        label="Precision",
    )
    recall_bars = axis.bar(
        [position + width / 2 for position in positions],
        recalls,
        width,
        color=["#68d391", "#b794f4", "#feb2b2"],
        label="Recall",
    )
    axis.set_ylim(0, 108)
    axis.set_xticks(positions, bands)
    axis.set_ylabel("Percent", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_xlabel("Grade band", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_title("Grade-Band Precision and Recall", fontsize=CHART_FONT_SIZES["title"], pad=14)
    axis.grid(axis="y", alpha=0.25)
    axis.legend(loc="lower right", fontsize=CHART_FONT_SIZES["legend"])
    axis.bar_label(precision_bars, labels=precision_labels, padding=3, fontsize=CHART_FONT_SIZES["annotation"])
    axis.bar_label(recall_bars, labels=recall_labels, padding=3, fontsize=CHART_FONT_SIZES["annotation"])
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def plot_letter_distance_metrics(answer_model_evaluation: dict[str, object], output_path: Path) -> None:
    """Show how exact and adjacent predictions compose Within 1 Letter."""

    splits = answer_model_evaluation.get("splits", {})
    test_split = splits.get("test", {}) if isinstance(splits, dict) else {}
    if not isinstance(test_split, dict):
        raise ValueError("Answer model evaluation does not define a test split.")
    exact = test_split.get("letter_accuracy")
    within_one = test_split.get("within_one_letter_accuracy")
    if not isinstance(exact, (int, float)) or not isinstance(within_one, (int, float)):
        raise ValueError("Test metrics must define letter_accuracy and within_one_letter_accuracy.")

    exact_percent = float(exact) * 100
    off_by_one_percent = max(0.0, float(within_one) - float(exact)) * 100
    beyond_one_percent = max(0.0, 1.0 - float(within_one)) * 100
    segments = (
        ("Exact Match", exact_percent, "#2f855a"),
        ("Off by 1", off_by_one_percent, "#4299e1"),
        ("More than 1", beyond_one_percent, "#c53030"),
    )

    figure, axis = plt.subplots(figsize=(8, 5))
    left = 0.0
    for label, value, color in segments:
        axis.barh([0], [value], left=left, color=color, height=0.42, label=label)
        if value >= 5:
            axis.text(left + value / 2, 0, f"{value:.0f}%", ha="center", va="center", color="white", fontweight="bold")
        left += value
    within_one_percent = float(within_one) * 100
    axis.axvline(within_one_percent, color="#742a2a", linestyle="--", linewidth=2)
    axis.annotate(
        f"Within 1 Letter: {within_one_percent:.1f}%",
        xy=(within_one_percent, 0.23),
        xytext=(within_one_percent - 3, 0.48),
        ha="right",
        fontsize=CHART_FONT_SIZES["annotation"],
        fontweight="bold",
    )
    axis.set_xlim(0, 100)
    axis.set_ylim(-0.6, 0.72)
    axis.set_yticks([])
    axis.set_xlabel("Percent of predictions", fontsize=CHART_FONT_SIZES["axis"])
    axis.set_title("Letter-Distance Accuracy", fontsize=CHART_FONT_SIZES["title"], pad=14)
    axis.grid(axis="x", alpha=0.25)
    axis.legend(loc="lower center", ncol=3, fontsize=CHART_FONT_SIZES["legend"])
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=160)
    plt.close(figure)

if __name__ == "__main__":
    main()
