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
    plot_question_coverage_artifacts,
)
from aws_certification_coach.mongodb import get_mongodb_database, mongodb_content_enabled, mongodb_database_name, mongodb_uri
from aws_certification_coach.questions.json_repository import DEFAULT_GENERATED_QUESTIONS_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/question_coverage.json"))
    parser.add_argument("--chart-output", type=Path, default=None)
    parser.add_argument("--chart-output-dir", type=Path, default=Path("release/metrics"))
    args = parser.parse_args()

    rows = _question_rows(args.questions)
    if not isinstance(rows, list):
        raise ValueError(f"Question file must contain a list: {args.questions}")
    metrics = measure_question_coverage([row for row in rows if isinstance(row, dict)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    chart_outputs = plot_question_coverage_artifacts(metrics, args.chart_output_dir)
    if args.chart_output is not None:
        plot_question_coverage(metrics, args.chart_output)
    print(json.dumps(metrics, indent=2))
    for name, path in chart_outputs.items():
        print(f"Question {name} coverage chart: {path}")
    if args.chart_output is not None:
        print(f"Question coverage chart: {args.chart_output}")

def _question_rows(path: Path) -> list[object]:
    if path.resolve() == DEFAULT_GENERATED_QUESTIONS_PATH.resolve() and mongodb_content_enabled():
        database = get_mongodb_database(mongodb_uri(), mongodb_database_name())
        rows = list(database["generated_questions"].find({}, {"_id": False}))
        if rows:
            return rows
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
