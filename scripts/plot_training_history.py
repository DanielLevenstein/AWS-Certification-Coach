#!/usr/bin/env python3
"""Plot partial-credit training history with pandas and Matplotlib."""

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
import pandas as pd


def plot_training_history(
    history_path: Path,
    output_path: Path,
    accuracy_output_path: Path | None = None,
) -> None:
    payload = json.loads(history_path.read_text(encoding="utf-8"))
    checkpoints = payload.get("checkpoints", [])
    frame = pd.DataFrame(checkpoints)
    required_columns = {"epoch", "mse", "mae"}
    if frame.empty or not required_columns.issubset(frame.columns):
        raise ValueError(f"Training history must contain {sorted(required_columns)}: {history_path}")

    frame = frame.sort_values("epoch").set_index("epoch")
    axis = frame[["mse", "mae"]].plot(
        marker="o",
        linewidth=2,
        figsize=(10, 6),
        color={"mse": "#d62728", "mae": "#1f77b4"},
    )
    axis.set_title("Partial-Credit Model Performance During Training")
    axis.set_xlabel("Training epoch")
    axis.set_ylabel("Error (lower is better)")
    axis.set_xscale("log")
    axis.set_xticks(frame.index)
    axis.set_xticklabels([str(int(epoch)) for epoch in frame.index])
    axis.set_ylim(bottom=0)
    axis.grid(True, alpha=0.25)
    axis.legend(["Mean squared error", "Mean absolute error"])
    axis.figure.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, dpi=160)
    plt.close(axis.figure)

    if accuracy_output_path is not None:
        _plot_curated_accuracy(frame, accuracy_output_path)


def _plot_curated_accuracy(frame: pd.DataFrame, output_path: Path) -> None:
    if "curated_grade_accuracy" not in frame.columns:
        raise ValueError("Training history does not contain curated_grade_accuracy.")
    accuracy = frame["curated_grade_accuracy"] * 100
    axis = accuracy.plot(
        marker="o",
        linewidth=2.5,
        figsize=(10, 6),
        color="#2ca02c",
    )
    axis.axhline(90, color="#d62728", linestyle="--", linewidth=2, label="Release target (90%)")
    axis.set_title("Curated Grade-Band Accuracy During Training")
    axis.set_xlabel("Training epoch")
    axis.set_ylabel("Grade-band accuracy (A/B, C/D, F)")
    axis.set_xscale("log")
    axis.set_xticks(frame.index)
    axis.set_xticklabels([str(int(epoch)) for epoch in frame.index])
    axis.set_ylim(0, 100)
    axis.grid(True, alpha=0.25)
    axis.legend(["Curated grade-band accuracy", "Release target (90%)"])
    for epoch, value in accuracy.items():
        axis.annotate(f"{value:.0f}%", (epoch, value), xytext=(0, 8), textcoords="offset points", ha="center")
    axis.figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    axis.figure.savefig(output_path, dpi=160)
    plt.close(axis.figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("release/metrics/training_history.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("release/metrics/training_performance.png"),
    )
    parser.add_argument(
        "--accuracy-output",
        type=Path,
        default=Path("release/metrics/curated_grade_accuracy.png"),
    )
    args = parser.parse_args()
    plot_training_history(args.history, args.output, args.accuracy_output)
    print(f"Training graph: {args.output}")
    print(f"Curated accuracy graph: {args.accuracy_output}")


if __name__ == "__main__":
    main()
