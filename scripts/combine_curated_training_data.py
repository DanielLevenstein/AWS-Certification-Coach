#!/usr/bin/env python3
"""Combine curated training data fragments into one JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_PATTERNS = (
    "curated_training_data.json",
    "curated_training_*.json",
    "curated_training_*.data",
    "user_feedback.*.json",
)


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
    seen_rows: set[str] = set()
    for path in input_paths:
        with path.open("r", encoding="utf-8") as input_file:
            rows = json.load(input_file)
        if not isinstance(rows, list):
            raise ValueError(f"Curated training data must be a JSON list: {path}")
        for index, row in enumerate(rows):
            _validate_curated_row(row, path, index)
            curated_row = json.dumps(_curated_row(row))
            if curated_row not in seen_rows:
                seen_rows.add(curated_row)
                combined_rows.append(json.loads(curated_row))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(combined_rows, indent=2) + "\n", encoding="utf-8")
    return len(input_paths), len(combined_rows)


def _validate_curated_row(row: object, path: Path, index: int) -> None:
    if not isinstance(row, dict):
        raise ValueError(f"Curated training row {index} must be a JSON object: {path}")
    if not str(row.get("question", "")).strip():
        raise ValueError(f"Curated training row {index} is missing full question text: {path}")


def _curated_row(row: dict) -> dict:
    allowed_fields = {
        "schema_version",
        "question",
        "exam_code",
        "reference_answer",
        "answer_given",
        "correct_rating",
        "rating_given",
        "correct_answer_text",
        "feedback_text",
    }
    curated = {key: value for key, value in row.items() if key in allowed_fields}
    
    # if original_multiple_choice answer is present add correct_answer_text to schema and update a version to v2 otherwise leave field out.
    original_mcq = row.get("original_multiple_choice", {})
    if isinstance(original_mcq, dict) and "correct_option_ids" in original_mcq:
        curated["correct_answer_id"] = original_mcq["correct_option_ids"]
        for option in original_mcq.get("options", []):
            if option["option_id"] in curated["correct_answer_id"]:
                curated["correct_answer_text"] = option["text"]
        curated["schema_version"] = 2
    ordered_keys = [
        "schema_version",
        "question",
        "exam_code",
        "reference_answer",
        "answer_given",
        "correct_rating",
        "rating_given",
        "correct_answer_text",
        "feedback_text",
    ]
    return {key: curated[key] for key in ordered_keys if key in curated}


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
