#!/usr/bin/env python3
"""Combine release chart PNGs into accuracy and question-coverage artifacts."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "release/metrics/.matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "release/metrics/.cache")

import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


CHART_FONT_SIZES = {
    "title": 20,
    "suptitle": 28,
}

DEFAULT_CHARTS = (
    ("Semantic Similarity", Path("release/semantic_accuracy.png")),
    ("Per-Grade Precision & Recall", Path("release/per_grade_metrics.png")),
    ("Grade Bands", Path("release/grade_band_metrics.png")),
    ("Certification Split", Path("release/question_certification_coverage.png")),
    ("Domain Coverage", Path("release/question_domain_coverage.png")),
    ("Question Category", Path("release/question_intent_coverage.png")),
)


def combine_accuracy_charts(charts: list[tuple[str, Path]], output: Path) -> None:
    _validate_charts(charts, {"Semantic Similarity", "Per-Grade Precision & Recall", "Grade Bands"})
    figure, axes = plt.subplots(1, 3, figsize=(24, 7), constrained_layout=True)
    _render_panels(figure, list(axes), charts, "AWS Certification Coach Grade Metrics")
    _save(figure, output)


def combine_question_coverage_charts(charts: list[tuple[str, Path]], output: Path) -> None:
    _validate_charts(charts, {"Certification Split", "Domain Coverage", "Question Category"})
    figure, axes = plt.subplots(1, 3, figsize=(24, 8), constrained_layout=True)
    _render_panels(figure, list(axes), charts, "AWS Certification Coach Question Coverage")
    _save(figure, output)


def _validate_charts(charts: list[tuple[str, Path]], required: set[str]) -> None:
    missing = [str(path) for _, path in charts if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing release chart input(s): {', '.join(missing)}")
    missing_titles = sorted(required - {title for title, _ in charts})
    if missing_titles:
        raise ValueError(f"Missing release chart panel(s): {', '.join(missing_titles)}")


def _render_panels(figure: object, axes: list[object], charts: list[tuple[str, Path]], title: str) -> None:
    for axis, (panel_title, path) in zip(axes, charts, strict=True):
        axis.imshow(mpimg.imread(path))
        axis.set_title(panel_title, fontsize=CHART_FONT_SIZES["title"], fontweight="bold", pad=12)
        axis.axis("off")
    figure.suptitle(
        title,
        fontsize=CHART_FONT_SIZES["suptitle"],
        fontweight="bold",
    )


def _save(figure: object, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-accuracy", type=Path, default=DEFAULT_CHARTS[0][1])
    parser.add_argument("--per-grade", type=Path, default=DEFAULT_CHARTS[1][1])
    parser.add_argument("--grade-bands", type=Path, default=DEFAULT_CHARTS[2][1])
    parser.add_argument("--certification-coverage", type=Path, default=DEFAULT_CHARTS[3][1])
    parser.add_argument("--domain-coverage", type=Path, default=DEFAULT_CHARTS[4][1])
    parser.add_argument("--intent-coverage", type=Path, default=DEFAULT_CHARTS[5][1])
    parser.add_argument("--accuracy-output", type=Path, default=Path("release/accuracy_metrics_chart.png"))
    parser.add_argument("--coverage-output", type=Path, default=Path("release/question_coverage_metrics_chart.png"))
    args = parser.parse_args()

    combine_accuracy_charts(
        [
            ("Semantic Similarity", args.semantic_accuracy),
            ("Grade Bands", args.grade_bands),
            ("Per-Grade Precision & Recall", args.per_grade),
        ],
        args.accuracy_output,
    )
    combine_question_coverage_charts(
        [
            ("Certification Split", args.certification_coverage),
            ("Domain Coverage", args.domain_coverage),
            ("Question Category", args.intent_coverage),
        ],
        args.coverage_output,
    )
    print(f"Accuracy metrics chart: {args.accuracy_output}")
    print(f"Question coverage chart: {args.coverage_output}")


if __name__ == "__main__":
    main()
