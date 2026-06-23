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
    answer_model_evaluation = _optional_read(metrics_dir / "answer_model_evaluation.json")
    answer_model_markdown = _optional_read_text(metrics_dir / "answer_model_evaluation.md")
    question_fidelity = _optional_read(metrics_dir / "question_fidelity.json")
    question_coverage = _optional_read(metrics_dir / "question_coverage.json")
    saved_model = training_metrics.get("saved_model", {}) if training_metrics else {}
    answer_form = saved_model.get("answer_form", training_metrics.get("answer_form", "unknown") if training_metrics else "unknown")
    calibration_count = saved_model.get("calibration_count", 0)
    exact_letter_accuracy = float(semantic.get("semantic_exact_letter_accuracy", semantic["semantic_grade_accuracy"]))
    grade_band_table = _grade_band_metrics_table(answer_model_evaluation)
    per_grade_table = _per_grade_metrics_table(answer_model_evaluation)
    return "\n".join(
        [
            "## Generated Release Metrics",
            "",
            "| Release | Legacy Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Within 1 Letter | Question Fidelity |",
            "|:--------|------------------:|-------------------:|----------------:|----------------------:|----------------:|------------------:|",
            f"| {release_label} | {semantic['semantic_grade_accuracy']:.2%} | "
            f"{semantic['semantic_precision']:.2%} | {semantic['semantic_recall']:.2%} | "
            f"{exact_letter_accuracy:.2%} | {_answer_within_one_letter_cell(answer_model_evaluation)} | "
            f"{_question_fidelity_cell(question_fidelity)} |",
            "",
            "## Grade Band Metrics",
            "",
            grade_band_table,
            "",
            "## Per Grade Metrics",
            "",
            per_grade_table,
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
            f"Semantic evaluation count: `{semantic.get('semantic_example_count', 0)}`",
            "Grade-band reporting uses the exclusive `A`, `BC`, and `DF` groups from `BandAccuracy`.",
            "Exact Letter Accuracy requires exact `A`, `B`, `C`, `D`, or `F` agreement.",
            "Within 1 Letter uses the ordered `A`, `B`, `C`, `D`, `F` scale.",
            "Legacy Semantic Precision and Recall retain the original `A`–`D` accepted and `F` rejected definition.",
            "Question fidelity is the release guardrail for generated-question concept and exam-style fidelity.",
            "",
            "## Answer Model Split Evaluation",
            "",
            answer_model_markdown or "Not run.",
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


def _optional_read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _question_fidelity_cell(question_fidelity: dict[str, object]) -> str:
    if "question_fidelity" not in question_fidelity:
        return "N/A"
    return f"{float(question_fidelity['question_fidelity']):.2f}%"


def _answer_within_one_letter_cell(answer_model_evaluation: dict[str, object]) -> str:
    splits = answer_model_evaluation.get("splits", {})
    if not isinstance(splits, dict):
        return "N/A"
    test_split = splits.get("test", {})
    if not isinstance(test_split, dict) or "within_one_letter_accuracy" not in test_split:
        return "N/A"
    return f"{float(test_split['within_one_letter_accuracy']):.2%}"


def _per_grade_metrics_table(answer_model_evaluation: dict[str, object]) -> str:
    splits = answer_model_evaluation.get("splits", {})
    test_split = splits.get("test", {}) if isinstance(splits, dict) else {}
    per_grade = test_split.get("per_grade", {}) if isinstance(test_split, dict) else {}
    if not isinstance(per_grade, dict):
        per_grade = {}
    lines = [
        "| Metric | A | B | C | D | F |",
        "|:-------|--:|--:|--:|--:|--:|",
    ]
    for label, key in (("Precision", "precision"), ("Recall", "recall"), ("F1", "f1")):
        cells = [_percentage_cell(per_grade.get(grade), key) for grade in GRADES]
        lines.append(f"| {label} | {' | '.join(cells)} |")
    support_cells = [_integer_cell(per_grade.get(grade), "support") for grade in GRADES]
    lines.append(f"| Support | {' | '.join(support_cells)} |")
    return "\n".join(lines)


def _grade_band_metrics_table(answer_model_evaluation: dict[str, object]) -> str:
    splits = answer_model_evaluation.get("splits", {})
    test_split = splits.get("test", {}) if isinstance(splits, dict) else {}
    per_band = test_split.get("per_grade_band", {}) if isinstance(test_split, dict) else {}
    if not isinstance(per_band, dict):
        per_band = {}
    bands = ("A", "BC", "DF")
    lines = [
        "| Metric | A | BC | DF |",
        "|:-------|--:|---:|---:|",
    ]
    for label, key in (("Precision", "precision"), ("Recall", "recall"), ("F1", "f1")):
        cells = [_percentage_cell(per_band.get(band), key) for band in bands]
        lines.append(f"| {label} | {' | '.join(cells)} |")
    support_cells = [_integer_cell(per_band.get(band), "support") for band in bands]
    lines.append(f"| Support | {' | '.join(support_cells)} |")
    return "\n".join(lines)


GRADES = ("A", "B", "C", "D", "F")


def _percentage_cell(metrics: object, key: str) -> str:
    if not isinstance(metrics, dict) or metrics.get(key) is None:
        return "N/A"
    return f"{float(metrics[key]):.2%}"


def _integer_cell(metrics: object, key: str) -> str:
    if not isinstance(metrics, dict) or metrics.get(key) is None:
        return "0"
    return str(int(metrics[key]))


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
