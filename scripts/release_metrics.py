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
    semantic = _read(metrics_dir / "semantic_similarity.json")
    classifier_test = _optional_read(metrics_dir / "semantic_classifier_test.json")
    comparison = _optional_read(metrics_dir / "answer_evaluator_comparison.json")
    question_fidelity = _optional_read(metrics_dir / "question_fidelity.json")
    question_coverage = _optional_read(metrics_dir / "question_coverage.json")
    classifier_metrics = classifier_test.get("metrics", classifier_test.get("test", {}))
    if not isinstance(classifier_metrics, dict):
        classifier_metrics = {}
    comparison_table = _comparison_table(comparison)
    per_grade_precision_table = _per_grade_precision_table(classifier_metrics)
    release_gate_note = _release_gate_note(classifier_test)
    return "\n".join(
        [
            "## Generated Release Metrics",
            "",
            "| Release | Evaluator | Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Within 1 Letter | Question Fidelity |",
            "|:--------|:----------|------------------:|-------------------:|----------------:|----------------------:|----------------:|------------------:|",
            f"| {release_label} | semantic_grade_classifier_v1 | {_metric_cell(classifier_metrics, 'semantic_accuracy')} | "
            f"{_metric_cell(classifier_metrics, 'semantic_precision')} | {_metric_cell(classifier_metrics, 'semantic_recall')} | "
            f"{_metric_cell(classifier_metrics, 'exact_letter_accuracy')} | {_metric_cell(classifier_metrics, 'within_one_letter_accuracy')} | "
            f"{_question_fidelity_cell(question_fidelity)} |",
            "",
            "## Classifier Diagnostics",
            "",
            "| Macro Precision | Macro Recall | Macro F1 | Ordinal MAE | Severe Error Rate | F Rejection Recall |",
            "|----------------:|-------------:|---------:|------------:|------------------:|-------------------:|",
            f"| {_metric_cell(classifier_metrics, 'macro_precision')} | {_metric_cell(classifier_metrics, 'macro_recall')} | "
            f"{_metric_cell(classifier_metrics, 'macro_f1')} | {_decimal_cell(classifier_metrics, 'ordinal_mae')} | "
            f"{_metric_cell(classifier_metrics, 'severe_error_rate')} | {_metric_cell(classifier_metrics, 'f_rejection_recall')} |",
            "",
            "## Per Grade Metrics",
            "",
            per_grade_precision_table,
            "",
            "## Migration Comparison",
            "",
            comparison_table,
            "",
            f"Question fidelity model: `{question_fidelity.get('model_name', 'not-run')}`",
            f"Developer source question count: `{question_fidelity.get('source_count', 0)}`",
            f"App question count: `{question_coverage.get('question_count', 0)}`",
            f"Question coverage domain count: `{question_coverage.get('domain_count', 0)}`",
            f"Question coverage concept count: `{question_coverage.get('concept_count', 0)}`",
            f"Question coverage intent count: `{question_coverage.get('question_intent_count', 0)}`",
            f"Top covered concepts: `{_coverage_names(question_coverage, 'top_concepts', limit=12)}`",
            f"Legacy curated semantic evaluation count: `{semantic.get('semantic_example_count', 0)}`",
            "Semantic Accuracy uses grade-band agreement (`A/B`, `C/D`, or `F`).",
            "Exact Letter Accuracy requires exact `A`, `B`, `C`, `D`, or `F` agreement.",
            "Within 1 Letter uses the ordered `A`, `B`, `C`, `D`, `F` scale.",
            "Semantic Precision and Recall treat `A`–`C` as accepted and `D`/`F` as failing.",
            "Legacy and candidate migration rows must use the same frozen benchmark.",
            release_gate_note,
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


def _metric_cell(metrics: dict[str, object], key: str) -> str:
    value = metrics.get(key)
    if value is None:
        return "N/A"
    return f"{float(value):.2%}"


def _decimal_cell(metrics: dict[str, object], key: str) -> str:
    value = metrics.get(key)
    return "N/A" if value is None else f"{float(value):.3f}"


def _comparison_table(comparison: dict[str, object]) -> str:
    evaluators = comparison.get("evaluators", {})
    if not isinstance(evaluators, dict) or not evaluators:
        return "Not run."
    lines = [
        "| Evaluator | Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Within 1 Letter |",
        "|:----------|------------------:|-------------------:|----------------:|----------------------:|----------------:|",
    ]
    for name in ("legacy_semantic_similarity", "semantic_grade_classifier_v1"):
        metrics = evaluators.get(name, {})
        if not isinstance(metrics, dict):
            continue
        lines.append(
            f"| {name} | {_metric_cell(metrics, 'semantic_accuracy')} | "
            f"{_metric_cell(metrics, 'semantic_precision')} | {_metric_cell(metrics, 'semantic_recall')} | "
            f"{_metric_cell(metrics, 'exact_letter_accuracy')} | {_metric_cell(metrics, 'within_one_letter_accuracy')} |"
        )
    return "\n".join(lines)


def _per_grade_precision_table(metrics: dict[str, object]) -> str:
    grades = ("A", "B", "C", "D", "F")
    per_grade = metrics.get("per_grade", {})
    if not isinstance(per_grade, dict):
        per_grade = {}
    cells = []
    for grade in grades:
        grade_metrics = per_grade.get(grade, {})
        cells.append(
            _metric_cell(grade_metrics, "precision")
            if isinstance(grade_metrics, dict)
            else "N/A"
        )
    cells.append(_metric_cell(metrics, "within_one_letter_accuracy"))
    return "\n".join(
        [
            "| Metric | A | B | C | D | F | Within 1 Letter |",
            "|:-------|--:|--:|--:|--:|--:|----------------:|",
            f"| Precision | {' | '.join(cells)} |",
        ]
    )


def _release_gate_note(classifier_test: dict[str, object]) -> str:
    gates = classifier_test.get("release_gates", {})
    if not isinstance(gates, dict) or "passed" not in gates:
        return "Local classifier release gates: `not-run`."
    if gates.get("passed") is True:
        return "Local classifier release gates: `passed`."
    failures = gates.get("failures", [])
    if not isinstance(failures, list):
        failures = []
    details = "; ".join(str(failure) for failure in failures) or "threshold failure"
    return f"Local classifier release gates: `failed` — {details}."


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
