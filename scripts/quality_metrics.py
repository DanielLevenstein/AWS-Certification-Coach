#!/usr/bin/env python3
"""Generate unit-test coverage and source complexity metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.release_metrics import measure_complexity, measure_coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("src/aws_certification_coach"))
    parser.add_argument("--tests", type=Path, default=Path("tests"))
    parser.add_argument("--output-dir", type=Path, default=Path("release/metrics"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    complexity = measure_complexity(args.source)
    coverage = measure_coverage(
        args.source,
        args.tests,
        ignore_paths=(Path("tests/deployment"), Path("tests/model_smoke")),
    )
    _write(args.output_dir / "complexity.json", complexity)
    _write(args.output_dir / "coverage.json", coverage)
    print(f"coverage={coverage['coverage']:.2%}")
    print(f"average_complexity={complexity['average_complexity']:.2f}")
    print(f"maximum_complexity={complexity['maximum_complexity']}")


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
