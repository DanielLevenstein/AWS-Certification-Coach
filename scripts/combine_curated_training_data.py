#!/usr/bin/env python3
"""Combine curated training data fragments into one JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.config import current_schema_version


DEFAULT_PATTERNS = (
    "curated_training_data.json",
    "curated_training_*.json",
    "curated_training_*.data",
    "user_feedback.*.json",
)


def combine_curated_training_data(config_dir: Path, output: Path, generated_dir: Path | None = None) -> tuple[int, int]:
    input_paths = curated_training_input_paths(config_dir, generated_dir)
    if not input_paths:
        patterns = ", ".join(DEFAULT_PATTERNS)
        raise FileNotFoundError(f"No curated training data found in {config_dir} matching {patterns}")
    combined_rows: list[object] = []
    seen_rows: set[tuple[str, str, str, str, str]] = set()
    for path in input_paths:
        with path.open("r", encoding="utf-8") as input_file:
            rows = json.load(input_file)
        if not isinstance(rows, list):
            raise ValueError(f"Curated training data must be a JSON list: {path}")
        for index, row in enumerate(rows):
            _validate_curated_row(row, path, index)
            curated = _curated_row(row)
            dedupe_key = _curated_row_dedupe_key(curated)
            if dedupe_key in seen_rows:
                continue
            seen_rows.add(dedupe_key)
            curated_row = json.dumps(curated)
            combined_rows.append(json.loads(curated_row))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(combined_rows, indent=2) + "\n", encoding="utf-8")
    return len(input_paths), len(combined_rows)


def curated_training_input_paths(config_dir: Path, generated_dir: Path | None = None) -> list[Path]:
    return sorted(
        {
            path
            for source_dir in _source_dirs(config_dir, generated_dir)
            for pattern in DEFAULT_PATTERNS
            for path in source_dir.glob(pattern)
            if path.is_file()
        }
    )


def _source_dirs(config_dir: Path, generated_dir: Path | None) -> tuple[Path, ...]:
    if generated_dir is None:
        return (config_dir,)
    return tuple(dict.fromkeys((config_dir, generated_dir)))


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
    
    # If original_multiple_choice is present, add correct_answer_text and default new rows to the configured feedback schema.
    original_mcq = row.get("original_multiple_choice", {})
    if isinstance(original_mcq, dict) and "correct_option_ids" in original_mcq:
        curated["correct_answer_id"] = original_mcq["correct_option_ids"]
        for option in original_mcq.get("options", []):
            if option["option_id"] in curated["correct_answer_id"]:
                curated["correct_answer_text"] = option["text"]
        curated.setdefault("schema_version", current_schema_version("USER_FEEDBACK_VERSION"))
    #TODO: Add generated_answer feedback to json
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


def _curated_row_dedupe_key(row: dict) -> tuple[str, str, str, str, str]:
    return (
        _normalized_text(row.get("question", "")),
        _normalized_text(row.get("reference_answer", "")),
        _normalized_text(row.get("answer_given", "")),
        str(row.get("correct_rating", "")).strip().upper(),
        str(row.get("rating_given", "")).strip().upper(),
    )


def _normalized_text(value: object) -> str:
    return " ".join(str(value).casefold().split())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=Path("config/data"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/curated/curated_training_data.json"),
    )
    parser.add_argument("--generated-dir", type=Path, default=Path("data/generated"))
    args = parser.parse_args()

    input_paths = curated_training_input_paths(args.config_dir, args.generated_dir)
    file_count, row_count = combine_curated_training_data(args.config_dir, args.output, args.generated_dir)
    print(f"Combined {row_count} rows from {file_count} files into {args.output}")
    print("Curated source files:")
    for path in input_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
