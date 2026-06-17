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
    parser.add_argument("--release-label", default="Current")
    parser.add_argument("--release-notes", type=Path, default=None)
    args = parser.parse_args()

    markdown = render_release_metrics(args.metrics_dir, release_label=args.release_label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    if args.release_notes is not None:
        update_release_notes(args.release_notes, markdown)
    print(markdown, end="")


def render_release_metrics(metrics_dir: Path, release_label: str = "Current") -> str:
    training = _read(metrics_dir / "training_history.json")["checkpoints"]
    training_metrics = _optional_read(metrics_dir / "training_metrics.json")
    model_evaluation = _optional_read(metrics_dir / "model_evaluation.json")
    semantic = _read(metrics_dir / "semantic_similarity.json")
    question_fidelity = _optional_read(metrics_dir / "question_fidelity.json")
    final = training[-1]
    saved_model = training_metrics.get("saved_model", {}) if training_metrics else {}
    saved_model_accuracy = _saved_model_accuracy(saved_model, model_evaluation, final)
    checkpoint_accuracy = final["curated_grade_accuracy"]
    answer_form = saved_model.get("answer_form", training_metrics.get("answer_form", "unknown") if training_metrics else "unknown")
    calibration_count = saved_model.get("calibration_count", 0)
    return "\n".join(
        [
            "# Latest Release Metrics",
            "",
            "| Release | Saved Model Accuracy | Training Accuracy | Semantic Accuracy | Semantic Precision | Semantic Recall | Question Fidelity |",
            "|:--------|---------------------:|------------------:|------------------:|-------------------:|----------------:|------------------:|",
            f"| {release_label} | {saved_model_accuracy:.2%} | {checkpoint_accuracy:.2%} | {semantic['semantic_grade_accuracy']:.2%} | "
            f"{semantic['semantic_precision']:.2%} | {semantic['semantic_recall']:.2%} | {_question_fidelity_cell(question_fidelity)} |",
            "",
            f"Saved model answer form: `{answer_form}`",
            f"Saved model calibration count: `{calibration_count}`",
            f"Question fidelity model: `{question_fidelity.get('model_name', 'not-run')}`",
            f"Question fidelity sample count: `{question_fidelity.get('sample_count', 0)}`",
            f"Developer source question count: `{question_fidelity.get('source_count', 0)}`",
            f"Developer generated question count: `{question_fidelity.get('generated_question_count', question_fidelity.get('sample_count', 0))}`",
            f"Semantic answer evaluation count: `{semantic.get('semantic_example_count', 0)}`",
            "",
            "Training curve: `training_performance.png`",
            "Curated grade-band accuracy (A/B, C/D, F): `curated_grade_accuracy.png`",
            "`semantic_similarity` diagnostic chart: `semantic_accuracy.png`",
            "Curated failure analysis: `curated_failure_report.md`",
            "",
            "Semantic precision is the release guardrail for the `semantic_similarity` model.",
            "Question fidelity is the release guardrail for generated-question concept and exam-style fidelity.",
            "Answer-scoring metrics come from the existing generated answer and curated answer benchmarks; question expansion quality is tracked separately by Question Fidelity.",
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


def _question_fidelity_cell(question_fidelity: dict[str, object]) -> str:
    if "question_fidelity" not in question_fidelity:
        return "N/A"
    return f"{float(question_fidelity['question_fidelity']):.2f}%"


def update_release_notes(release_notes: Path, markdown: str) -> None:
    start_marker = "<!-- release-metrics:start -->"
    end_marker = "<!-- release-metrics:end -->"
    generated_block = f"{start_marker}\n{markdown.rstrip()}\n{end_marker}\n"
    content = release_notes.read_text(encoding="utf-8") if release_notes.exists() else ""
    if start_marker in content and end_marker in content:
        before, remainder = content.split(start_marker, 1)
        _, after = remainder.split(end_marker, 1)
        release_notes.write_text(before + generated_block + after.lstrip("\n"), encoding="utf-8")
        return
    separator = "\n" if content.endswith("\n") or not content else "\n\n"
    release_notes.write_text(content + separator + generated_block, encoding="utf-8")


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
