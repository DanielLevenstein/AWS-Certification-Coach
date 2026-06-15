#!/usr/bin/env python3
"""Consolidate generated release metrics into Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-dir", type=Path, default=Path("release/metrics"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/summary.md"))
    args = parser.parse_args()

    training = _read(args.metrics_dir / "training_history.json")["checkpoints"]
    coverage = _read(args.metrics_dir / "coverage.json")
    complexity = _read(args.metrics_dir / "complexity.json")
    final = training[-1]
    markdown = "\n".join(
        [
            "# Release Metrics",
            "",
            "| Unit coverage | Average complexity | Maximum complexity | Final training MSE | Final training MAE | Curated grade-band accuracy |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| {coverage['coverage']:.2%} | {complexity['average_complexity']:.2f} | "
            f"{complexity['maximum_complexity']} | {final['mse']:.4f} | {final['mae']:.4f} | "
            f"{final['curated_grade_accuracy']:.2%} |",
            "",
            "Training curve: `training_performance.png`",
            "Curated grade-band accuracy (A/B, C/D, F): `curated_grade_accuracy.png`",
            "Curated failure analysis: `curated_failure_report.md`",
        ]
    ) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(markdown, end="")


def _read(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


if __name__ == "__main__":
    main()
