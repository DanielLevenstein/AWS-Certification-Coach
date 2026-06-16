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
    training_metrics = _optional_read(metrics_dir / "training_metrics.json")
    model_evaluation = _optional_read(metrics_dir / "model_evaluation.json")
    semantic = _read(metrics_dir / "semantic_similarity.json")
    final = training[-1]
    saved_model = training_metrics.get("saved_model", {}) if training_metrics else {}
    saved_model_accuracy = _saved_model_accuracy(saved_model, model_evaluation, final)
    checkpoint_accuracy = final["curated_grade_accuracy"]
    answer_form = saved_model.get("answer_form", training_metrics.get("answer_form", "unknown") if training_metrics else "unknown")
    calibration_count = saved_model.get("calibration_count", 0)
    return "\n".join(
        [
            "# Release Metrics",
            "",
            "| Saved model curated accuracy | Training checkpoint accuracy | Semantic diagnostic accuracy | Semantic precision | Semantic recall |",
            "| ---: | ---: | ---: | ---: | ---: |",
            f"| {saved_model_accuracy:.2%} | {checkpoint_accuracy:.2%} | {semantic['semantic_grade_accuracy']:.2%} | "
            f"{semantic['semantic_precision']:.2%} | {semantic['semantic_recall']:.2%} |",
            "",
            f"Saved model answer form: `{answer_form}`",
            f"Saved model calibration count: `{calibration_count}`",
            "",
            "Training curve: `training_performance.png`",
            "Curated grade-band accuracy (A/B, C/D, F): `curated_grade_accuracy.png`",
            "Curated failure analysis: `curated_failure_report.md`",
            "",
            "Saved model accuracy is the release gate for the trained regressor. Semantic metrics are diagnostic only.",
            "Precision and recall treat A/B and C/D as accepted answers and F as rejected.",
        ]
    ) + "\n"


def _read(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def _optional_read(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return _read(path)


def _saved_model_accuracy(
    saved_model: dict[str, object],
    model_evaluation: dict[str, object],
    final_checkpoint: dict[str, object],
) -> float:
    if "curated_grade_accuracy" in saved_model:
        return float(saved_model["curated_grade_accuracy"])
    rubric = model_evaluation.get("rubric_adherence", {}) if model_evaluation else {}
    if isinstance(rubric, dict) and "grade_accuracy" in rubric:
        return float(rubric["grade_accuracy"])
    return float(final_checkpoint["curated_grade_accuracy"])


if __name__ == "__main__":
    main()
