#!/usr/bin/env python3
"""Root-level helpers for the three independent quality suites."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run_unit_tests(extra_args: list[str] | None = None) -> None:
    _run([sys.executable, "-m", "pytest", "tests", *(extra_args or [])])


def run_model_evaluation(extra_args: list[str] | None = None) -> None:
    _run([sys.executable, "scripts/model_evaluation.py", *(extra_args or [])])


def run_release_metrics(extra_args: list[str] | None = None) -> None:
    del extra_args
    _run(
        [
            sys.executable,
            "scripts/train_answer_accuracy.py",
            "--eval-mode",
            "training",
            "--output",
            "release/metrics/answer_regressor_model.json",
            "--metrics-output",
            "release/metrics/training_metrics.json",
        ]
    )
    _run([sys.executable, "scripts/plot_training_history.py"])
    _run([sys.executable, "scripts/curated_failure_report.py"])
    _run([sys.executable, "scripts/semantic_similarity_evaluation.py"])
    _run([sys.executable, "scripts/quality_metrics.py"])
    _run([sys.executable, "scripts/release_metrics.py"])


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
