#!/usr/bin/env python3
"""Evaluate the saved answer regression model across generated data splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel, evaluate_regression_model
from aws_certification_coach.training.dataset import AnswerRegressionExample, load_answer_regression_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


DEFAULT_SPLITS = {
    "train": Path("data/generated/questions_with_answers_training.json"),
    "validation": Path("data/generated/questions_with_answers_validation.json"),
    "test": Path("data/generated/questions_with_answers_test.json"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=Path("models/answer_regressor_model.json"))
    parser.add_argument("--train-data", type=Path, default=DEFAULT_SPLITS["train"])
    parser.add_argument("--validation-data", type=Path, default=DEFAULT_SPLITS["validation"])
    parser.add_argument("--test-data", type=Path, default=DEFAULT_SPLITS["test"])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--table-output", type=Path, default=None)
    args = parser.parse_args()

    model = AnswerRegressionModel.load(args.model)
    splits = {
        "train": args.train_data,
        "validation": args.validation_data,
        "test": args.test_data,
    }
    report = evaluate_model_splits(model, splits)
    payload = json.dumps(report, indent=2) + "\n"
    json_output = args.json_output or args.output
    if json_output is not None:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(payload, encoding="utf-8")
    table = render_markdown_table(report)
    if args.table_output is not None:
        args.table_output.parent.mkdir(parents=True, exist_ok=True)
        args.table_output.write_text(table + "\n", encoding="utf-8")
    print(table)
    print(payload, end="")


def evaluate_model_splits(
    model: AnswerRegressionModel,
    split_paths: dict[str, Path],
) -> dict[str, object]:
    extractor = AnswerFeatureExtractor(answer_form=model.answer_form)
    return {
        "model": {
            "answer_form": model.answer_form,
            "feature_count": len(model.feature_names),
            "extractor_feature_count": len(extractor.feature_names),
            "feature_mismatch": len(model.feature_names) != len(extractor.feature_names),
            "calibration_count": len(model.calibrations),
        },
        "splits": {
            name: evaluate_split(model, path, extractor)
            for name, path in split_paths.items()
        },
    }


def evaluate_split(
    model: AnswerRegressionModel,
    path: Path,
    extractor: AnswerFeatureExtractor,
) -> dict[str, object]:
    examples = load_answer_regression_examples(path)
    metrics = evaluate_regression_model(model, [], examples, extractor)
    grade_metrics = _grade_metrics(model, examples, extractor)
    return {
        "path": str(path),
        **metrics,
        **grade_metrics,
    }


def _grade_metrics(
    model: AnswerRegressionModel,
    examples: list[AnswerRegressionExample],
    extractor: AnswerFeatureExtractor,
) -> dict[str, object]:
    exact_matches = 0
    within_one_letter = 0
    total = len(examples)
    confusion: dict[str, dict[str, int]] = {}
    for example in examples:
        predicted = score_to_letter(round(model.predict(extractor.extract(example.question, example.answer)) * 100))
        expected = score_to_letter(round(example.rating * 100))
        exact_matches += int(predicted == expected)
        within_one_letter += int(abs(_letter_index(predicted) - _letter_index(expected)) <= 1)
        confusion.setdefault(expected, {})
        confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1
    return {
        "letter_accuracy": exact_matches / max(1, total),
        "within_one_letter_accuracy": within_one_letter / max(1, total),
        "letter_confusion": {
            expected: dict(sorted(predictions.items()))
            for expected, predictions in sorted(confusion.items())
        },
    }


def _letter_index(letter: str) -> int:
    return ["F", "D", "C", "B", "A"].index(letter)


def render_markdown_table(report: dict[str, object]) -> str:
    lines = [
        "| Split | Examples | Within 1 Letter | Exact Letter | MAE | MSE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    splits = report.get("splits", {})
    if not isinstance(splits, dict):
        return "\n".join(lines)
    for split_name in ("train", "validation", "test"):
        split = splits.get(split_name)
        if not isinstance(split, dict):
            continue
        lines.append(
            "| {split} | {examples} | {within} | {exact} | {mae} | {mse} |".format(
                split=_display_split_name(split_name),
                examples=int(split.get("example_count", 0)),
                within=_percent(split.get("within_one_letter_accuracy", 0.0)),
                exact=_percent(split.get("letter_accuracy", 0.0)),
                mae=_decimal(split.get("mae", 0.0)),
                mse=_decimal(split.get("mse", 0.0)),
            )
        )
    return "\n".join(lines)


def _display_split_name(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("_"))


def _percent(value: object) -> str:
    return f"{float(value) * 100:.1f}%"


def _decimal(value: object) -> str:
    return f"{float(value):.4f}"


if __name__ == "__main__":
    main()
