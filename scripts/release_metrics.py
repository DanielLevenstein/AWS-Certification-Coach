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
    parser.add_argument("--strict-grading", action="store_true")
    args = parser.parse_args()

    markdown = render_release_metrics(
        args.metrics_dir,
        release_label=args.release_label,
        strict_grading=args.strict_grading,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    if args.release_notes is not None:
        update_release_notes(args.release_notes, markdown)
    print(markdown, end="")


def render_release_metrics(
    metrics_dir: Path,
    release_label: str = "Current",
    strict_grading: bool = False,
) -> str:
    training_metrics = _optional_read(metrics_dir / "training_metrics.json")
    semantic = _read(metrics_dir / "semantic_similarity.json")
    question_fidelity = _optional_read(metrics_dir / "question_fidelity.json")
    question_coverage = _optional_read(metrics_dir / "question_coverage.json")
    saved_model = training_metrics.get("saved_model", {}) if training_metrics else {}
    answer_form = saved_model.get("answer_form", training_metrics.get("answer_form", "unknown") if training_metrics else "unknown")
    calibration_count = saved_model.get("calibration_count", 0)
    exact_letter_accuracy = float(semantic.get("semantic_exact_letter_accuracy", semantic["semantic_grade_accuracy"]))
    return "\n".join(
        [
            "## Generated Release Metrics",
            "",
            "| Release | Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Question Fidelity |",
            "|:--------|------------------:|-------------------:|----------------:|----------------------:|------------------:|",
            f"| {release_label} | {semantic['semantic_grade_accuracy']:.2%} | "
            f"{semantic['semantic_precision']:.2%} | {semantic['semantic_recall']:.2%} | "
            f"{exact_letter_accuracy:.2%} | {_question_fidelity_cell(question_fidelity)} |",
            "",
            f"Saved model answer form: `{answer_form}`",
            f"Saved model calibration count: `{calibration_count}`",
            f"Question fidelity model: `{question_fidelity.get('model_name', 'not-run')}`",
            f"Developer source question count: `{question_fidelity.get('source_count', 0)}`",
            f"App question count: `{question_coverage.get('question_count', 0)}`",
            f"Question coverage domain count: `{question_coverage.get('domain_count', 0)}`",
            f"Question coverage concept count: `{question_coverage.get('concept_count', 0)}`",
            f"Question coverage intent count: `{question_coverage.get('question_intent_count', 0)}`",
            f"Top covered concepts: `{_coverage_names(question_coverage, 'top_concepts', limit=12)}`",
            f"Semantic answer evaluation count: `{semantic.get('semantic_example_count', 0)}`",
            "Semantic Accuracy uses grade-band agreement (`A/B`, `C/D`, or `F`).",
            "Exact Letter Accuracy requires exact `A`, `B`, `C`, `D`, or `F` agreement.",
            "Semantic precision has a 90% release guardrail for the `semantic_similarity` model.",
            "Question fidelity is the release guardrail for generated-question concept and exam-style fidelity.",
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


def _coverage_names(question_coverage: dict[str, object], key: str, limit: int | None = None) -> str:
    rows = question_coverage.get(key, [])
    if not isinstance(rows, list):
        return "not-run"
    names = [
        str(row.get("name", "")).strip()
        for row in rows[:limit]
        if isinstance(row, dict) and str(row.get("name", "")).strip()
    ]
    return ", ".join(names) if names else "not-run"


def _strict_grading_label(strict_grading: bool) -> str:
    return "exact-letter" if strict_grading else "standard"


def _answer_metric_note(strict_grading: bool) -> str:
    if strict_grading:
        return "Answer-scoring accuracy requires exact `A`, `B`, `C`, `D`, or `F` agreement; precision and recall remain accepted-answer diagnostics."
    return "Answer-scoring metrics come from the existing generated answer and curated answer benchmarks; question expansion quality is tracked separately by Question Fidelity."


def _release_file_stem(release_label: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "_" for character in release_label)


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


if __name__ == "__main__":
    main()
