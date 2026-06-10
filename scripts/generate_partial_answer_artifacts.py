"""Refresh partial-credit answer sections inside combined question artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_sample_training_artifacts import _partial_examples


DEFAULT_ARTIFACTS = [
    Path("data/training/questions_with_answers_generated.json"),
    Path("data/verification/questions_with_answers_holdout.json"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", nargs="*", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()

    for artifact in args.artifacts:
        rows = json.loads(artifact.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"Combined question artifact must be a JSON list: {artifact}")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Combined question rows must be objects: {artifact}")
            service_name = _service_name(row)
            original = row.get("original_multiple_choice", {})
            question_text = str(original.get("question", row.get("question", ""))) if isinstance(original, dict) else str(row.get("question", ""))
            row["partial_answers"] = _partial_examples(
                str(row["question_id"]),
                service_name,
                [str(concept) for concept in row.get("key_concepts", [])],
                question_text,
            )
        artifact.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        print(f"Refreshed partial answers for {len(rows)} questions in {artifact}.")


def _service_name(row: dict) -> str:
    original = row.get("original_multiple_choice", {})
    options = original.get("options", []) if isinstance(original, dict) else []
    correct_ids = set(original.get("correct_option_ids", [])) if isinstance(original, dict) else set()
    for option in options:
        if isinstance(option, dict) and option.get("option_id") in correct_ids:
            return _normalize_service_name(str(option.get("text", "")))
    return _normalize_service_name(str(row.get("reference_answer", "")))


def _normalize_service_name(value: str) -> str:
    value = value.strip().rstrip(".")
    for prefix in ("Use ", "Attach ", "Deploy "):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    if " with " in value:
        value = value.split(" with ", 1)[0]
    if " to " in value:
        value = value.split(" to ", 1)[0]
    return value.strip()


if __name__ == "__main__":
    main()
