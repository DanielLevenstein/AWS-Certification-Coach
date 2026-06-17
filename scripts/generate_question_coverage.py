#!/usr/bin/env python3
"""Generate question-bank coverage metrics and chart artifacts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "release/metrics/.matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "release/metrics/.cache")

from aws_certification_coach.release_metrics.question_coverage import (
    measure_question_coverage,
    plot_question_coverage,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/question_coverage.json"))
    parser.add_argument("--chart-output", type=Path, default=Path("release/metrics/question_coverage.png"))
    args = parser.parse_args()

    rows = json.loads(args.questions.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"Question file must contain a list: {args.questions}")
    metrics = measure_question_coverage([row for row in rows if isinstance(row, dict)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    plot_question_coverage(metrics, args.chart_output)
    print(json.dumps(metrics, indent=2))
    print(f"Question coverage chart: {args.chart_output}")


if __name__ == "__main__":
    main()
