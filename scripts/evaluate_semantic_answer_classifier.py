#!/usr/bin/env python3
"""Final-report evaluation for the saved local semantic grade classifier."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.model_evaluation.grade_metrics import GRADES, evaluate_release_gates
from aws_certification_coach.training.dataset import load_answer_regression_examples, question_signature
from aws_certification_coach.training.semantic_grade_classifier import (
    SemanticAnswerFeatureExtractor,
    SemanticGradeClassifier,
    evaluate_classifier,
)


DEFAULT_TEST_DATA = Path("data/generated/questions_with_answers_test.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoder", default="models/huggingface/all-MiniLM-L6-v2")
    parser.add_argument("--classifier", type=Path, default=Path("models/answer_semantic_classifier.json"))
    parser.add_argument("--test-data", type=Path, default=DEFAULT_TEST_DATA)
    parser.add_argument("--output", type=Path, default=Path("metrics/semantic_classifier_test.json"))
    parser.add_argument("--chart-output", type=Path, default=None)
    parser.add_argument("--per-grade-precision-chart-output", type=Path, default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Write metrics without failing when the frozen v3 release gates are not met.",
    )
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    examples = load_answer_regression_examples(args.test_data)
    encoder = SentenceTransformer(args.encoder, device=args.device)
    extractor = SemanticAnswerFeatureExtractor(encoder)
    features = extractor.extract_many([(row.question, row.answer) for row in examples])
    labels = [score_to_letter(round(row.rating * 100)) for row in examples]
    classifier = SemanticGradeClassifier.load(args.classifier)
    results = evaluate_classifier(classifier, features, labels)
    gates = evaluate_release_gates(results)
    metrics = {
        "metrics_schema_version": 4,
        "evaluator": {
            "name": "semantic_grade_classifier_v1",
            "feature_version": classifier.feature_version,
            "encoder": args.encoder,
        },
        "benchmark": {
            "name": "v3_final_test",
            "path": str(args.test_data),
            "manifest_sha256": hashlib.sha256(args.test_data.read_bytes()).hexdigest(),
            "example_count": len(examples),
            "question_family_count": len({question_signature(row.question) for row in examples}),
            "support_by_grade": {grade: labels.count(grade) for grade in GRADES},
        },
        "metrics": results,
        "per_grade": results["per_grade"],
        "confusion_matrix": results["confusion_matrix"],
        "release_gates": gates,
        "test": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    if args.chart_output is not None:
        plot_classifier_metrics(results, args.chart_output)
    if args.per_grade_precision_chart_output is not None:
        plot_per_grade_precision(results, args.per_grade_precision_chart_output)
    print(json.dumps(metrics, indent=2))
    if not args.report_only and not gates["passed"]:
        raise SystemExit("Final test release gates failed: " + "; ".join(gates["failures"]))


def plot_classifier_metrics(metrics: dict[str, object], output: Path) -> None:
    """Render the honest classifier metrics used by release notes."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [
        "Within 1 Letter",
        "Semantic Accuracy",
        "Semantic Precision",
        "Semantic Recall",
        "Exact Letter",
    ]
    keys = [
        "within_one_letter_accuracy",
        "semantic_accuracy",
        "semantic_precision",
        "semantic_recall",
        "exact_letter_accuracy",
    ]
    values = [float(metrics[key]) * 100 for key in keys]
    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(labels, values, color=["#17becf", "#2ca02c", "#1f77b4", "#9467bd", "#ff7f0e"])
    axis.axhline(90, color="#d62728", linestyle="--", label="Within 1 letter gate (>90%)")
    axis.set_ylim(0, 105)
    axis.set_ylabel("Percent")
    axis.set_title("Local Semantic Classifier — Final Test")
    axis.tick_params(axis="x", rotation=15)
    axis.legend(loc="lower left")
    axis.bar_label(bars, labels=[f"{value:.1f}%" for value in values], padding=3)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def plot_per_grade_precision(metrics: dict[str, object], output: Path) -> None:
    """Render precision for each A/B/C/D/F grade."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    per_grade = metrics.get("per_grade", {})
    if not isinstance(per_grade, dict):
        raise ValueError("Classifier metrics must include per_grade results.")
    within_one = metrics.get("within_one_letter_accuracy")
    if not isinstance(within_one, (int, float)):
        raise ValueError("Classifier metrics do not define within_one_letter_accuracy.")
    labels = ["Within 1 Letter", *GRADES]
    values = [float(within_one) * 100]
    for grade in GRADES:
        grade_metrics = per_grade.get(grade, {})
        if not isinstance(grade_metrics, dict) or grade_metrics.get("precision") is None:
            raise ValueError(f"Classifier metrics do not define precision for grade {grade}.")
        values.append(float(grade_metrics["precision"]) * 100)
    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(
        labels,
        values,
        color=["#17becf", "#2f855a", "#4299e1", "#805ad5", "#ed8936", "#c53030"],
    )
    axis.axhline(90, color="#d62728", linestyle="--", label="Within 1 letter gate (>90%)")
    axis.set_ylim(0, 105)
    axis.set_ylabel("Precision (%)")
    axis.set_xlabel("Predicted grade")
    axis.set_title("Per-Grade Precision and Within-One Accuracy — Final Test")
    axis.tick_params(axis="x", rotation=12)
    axis.legend(loc="lower left")
    axis.bar_label(bars, labels=[f"{value:.1f}%" for value in values], padding=3)
    axis.grid(axis="y", alpha=0.2)
    figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
