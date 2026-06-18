#!/usr/bin/env python3
"""Combine release chart PNGs into one release-note artifact."""

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


DEFAULT_CHARTS = (
    ("Semantic Accuracy", Path("release/semantic_accuracy.png")),
    ("Certification Split", Path("release/question_certification_coverage.png")),
    ("Domain Coverage", Path("release/question_domain_coverage.png")),
    ("Question Intent Mix", Path("release/question_intent_coverage.png")),
)


def combine_release_charts(charts: list[tuple[str, Path]], output: Path) -> None:
    missing = [str(path) for _, path in charts if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing release chart input(s): {', '.join(missing)}")

    figure, axes = plt.subplots(2, 2, figsize=(18, 14), constrained_layout=True)
    for axis, (title, path) in zip(axes.flat, charts):
        axis.imshow(mpimg.imread(path))
        axis.set_title(title, fontsize=15, fontweight="bold", pad=10)
        axis.axis("off")

    figure.suptitle("AWS Certification Coach Release Metrics", fontsize=22, fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-accuracy", type=Path, default=DEFAULT_CHARTS[0][1])
    parser.add_argument("--certification-coverage", type=Path, default=DEFAULT_CHARTS[1][1])
    parser.add_argument("--domain-coverage", type=Path, default=DEFAULT_CHARTS[2][1])
    parser.add_argument("--intent-coverage", type=Path, default=DEFAULT_CHARTS[3][1])
    parser.add_argument("--output", type=Path, default=Path("release/release_metrics_chart.png"))
    args = parser.parse_args()

    combine_release_charts(
        [
            ("Semantic Accuracy", args.semantic_accuracy),
            ("Certification Split", args.certification_coverage),
            ("Domain Coverage", args.domain_coverage),
            ("Question Intent Mix", args.intent_coverage),
        ],
        args.output,
    )
    print(f"Combined release charts: {args.output}")


if __name__ == "__main__":
    main()
