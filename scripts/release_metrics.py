"""Print consolidated model performance metrics for release notes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_CLASSIFIER_METRICS = Path("models/answer_classifier_metrics.json")
DEFAULT_PARTIAL_METRICS = Path("models/partial_answer_regressor_metrics.json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--classifier-metrics", type=Path, default=DEFAULT_CLASSIFIER_METRICS)
    parser.add_argument("--partial-metrics", type=Path, default=DEFAULT_PARTIAL_METRICS)
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    metrics = build_release_metrics(args.classifier_metrics, args.partial_metrics)
    if args.format == "json":
        print(json.dumps(metrics, indent=2))
    else:
        print(format_markdown(metrics))


def build_release_metrics(classifier_path: Path, partial_path: Path) -> dict[str, object]:
    classifier = _read_json(classifier_path)
    partial = _read_json(partial_path)
    return {
        "classifier": {
            "accuracy": classifier["accuracy"],
            "precision": classifier["precision"],
            "recall": classifier["recall"],
            "example_count": classifier["example_count"],
            "eval_mode": classifier["eval_mode"],
            "suspicious_accuracy": classifier.get("suspicious_accuracy", False),
            "true_positive": classifier["true_positive"],
            "false_positive": classifier["false_positive"],
            "true_negative": classifier["true_negative"],
            "false_negative": classifier["false_negative"],
        },
        "partial_credit_regressor": {
            "mse": partial["mse"],
            "mae": partial["mae"],
            "example_count": partial["example_count"],
            "eval_mode": partial["eval_mode"],
        },
    }


def format_markdown(metrics: dict[str, object]) -> str:
    classifier = metrics["classifier"]
    partial = metrics["partial_credit_regressor"]
    return "\n".join(
        [
            "| Release | Accuracy | Precision | Recall | Full Examples | MSE | MAE | Partial Examples | TP | FP | TN | FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| Release 1 | {_percent(classifier['accuracy'])} | {_percent(classifier['precision'])} | {_percent(classifier['recall'])} | "
            f"{classifier['example_count']} | {partial['mse']:.4f} | {partial['mae']:.4f} | {partial['example_count']} | "
            f"{classifier['true_positive']} | {classifier['false_positive']} | {classifier['true_negative']} | {classifier['false_negative']} |",
        ]
    )


def _read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Metrics file must contain a JSON object: {path}")
    return payload


def _percent(value: object) -> str:
    return f"{float(value) * 100:.2f}%"


if __name__ == "__main__":
    main()
