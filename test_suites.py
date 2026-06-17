#!/usr/bin/env python3
"""Root-level helpers for the three independent quality suites."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run_unit_tests(extra_args: list[str] | None = None) -> None:
    _run([sys.executable, "-m", "pytest", "tests", *(extra_args or [])])


def run_model_evaluation(extra_args: list[str] | None = None) -> None:
    _run([sys.executable, "scripts/model_evaluation.py", *(extra_args or [])])


def run_release_metrics(extra_args: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-label", default="Current")
    parser.add_argument("--release-notes", default=None)
    parser.add_argument("--metrics-dir", type=Path, default=None)
    args = parser.parse_args(extra_args or [])
    metrics_dir = args.metrics_dir or timestamped_metrics_dir()
    _run(
        [
            sys.executable,
            "scripts/train_answer_accuracy.py",
            "--eval-mode",
            "training",
            "--output",
            str(metrics_dir / "answer_regressor_model.json"),
            "--metrics-output",
            str(metrics_dir / "training_metrics.json"),
            "--history-output",
            str(metrics_dir / "training_history.json"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/plot_training_history.py",
            "--history",
            str(metrics_dir / "training_history.json"),
            "--output",
            str(metrics_dir / "training_performance.png"),
            "--accuracy-output",
            str(metrics_dir / "curated_grade_accuracy.png"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/curated_failure_report.py",
            "--model",
            str(metrics_dir / "answer_regressor_model.json"),
            "--output",
            str(metrics_dir / "curated_failure_report.md"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/semantic_similarity_evaluation.py",
            "--output",
            str(metrics_dir / "semantic_similarity.json"),
            "--chart-output",
            str(metrics_dir / "semantic_accuracy.png"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/question_fidelity_evaluation.py",
            "--output",
            str(metrics_dir / "question_fidelity.json"),
        ]
    )
    _run([sys.executable, "scripts/quality_metrics.py", "--output-dir", str(metrics_dir)])
    release_metrics_command = [
        sys.executable,
        "scripts/release_metrics.py",
        "--metrics-dir",
        str(metrics_dir),
        "--output",
        str(metrics_dir / "summary.md"),
        "--release-label",
        args.release_label,
    ]
    if args.release_notes is not None:
        release_metrics_command.extend(["--release-notes", args.release_notes])
    _run(release_metrics_command)
    print(f"Release metrics directory: {metrics_dir}")


def timestamped_metrics_dir() -> Path:
    return Path("metrics") / datetime.now().strftime("%Y%m%d_%H%M%S")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", choices=["unit", "model", "release"])
    args, extra_args = parser.parse_known_args()
    {
        "unit": run_unit_tests,
        "model": run_model_evaluation,
        "release": run_release_metrics,
    }[args.suite](extra_args)


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
