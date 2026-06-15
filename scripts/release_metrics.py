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

    markdown = render_release_metrics(args.metrics_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(markdown, end="")


def render_release_metrics(metrics_dir: Path) -> str:
    training = _read(metrics_dir / "training_history.json")["checkpoints"]
    final = training[-1]
    return "\n".join(
        [
            "# Release Metrics",
            "",
            "| Curated grade-band accuracy | Generated-label MSE | Semantic-aware grading | Generated-label MAE |",
            "| ---: | ---: | --- | ---: |",
            f"| {final['curated_grade_accuracy']:.2%} | {final['mse']:.4f} | TBD | "
            f"{final['mae']:.4f} |",
            "",
            "Training curve: `training_performance.png`",
            "Curated grade-band accuracy (A/B, C/D, F): `curated_grade_accuracy.png`",
            "Curated failure analysis: `curated_failure_report.md`",
            "",
            "Regression MSE/MAE measure numeric fit against generated/feedback labels; use curated grade-band accuracy as the primary release signal until semantic-aware grading is implemented.",
        ]
    ) + "\n"


def _read(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


if __name__ == "__main__":
    main()
