#!/usr/bin/env python3
"""Combine curated training data fragments into one JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_PATTERNS = ("curated_training_*.data", "curated_training_*.json")


def combine_curated_training_data(config_dir: Path, output: Path) -> tuple[int, int]:
    input_paths = sorted(
        {
            path
            for pattern in DEFAULT_PATTERNS
            for path in config_dir.glob(pattern)
            if path.is_file()
        }
    )
    if not input_paths:
        patterns = ", ".join(DEFAULT_PATTERNS)
        raise FileNotFoundError(f"No curated training data found in {config_dir} matching {patterns}")

    combined_rows: list[object] = []
    for path in input_paths:
        with path.open("r", encoding="utf-8") as input_file:
            rows = json.load(input_file)
        if not isinstance(rows, list):
            raise ValueError(f"Curated training data must be a JSON list: {path}")
        combined_rows.extend(rows)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(combined_rows, indent=2) + "\n", encoding="utf-8")
    return len(input_paths), len(combined_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=Path("config"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/curated/curated_training_data.json"),
    )
    args = parser.parse_args()

    file_count, row_count = combine_curated_training_data(args.config_dir, args.output)
    print(f"Combined {row_count} rows from {file_count} files into {args.output}")


if __name__ == "__main__":
    main()
