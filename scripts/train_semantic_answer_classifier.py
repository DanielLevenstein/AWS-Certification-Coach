#!/usr/bin/env python3
"""Train the local A/B/C/D/F head over SentenceTransformer features."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.dataset import load_answer_regression_examples
from aws_certification_coach.training.semantic_grade_classifier import (
    SemanticAnswerFeatureExtractor,
    evaluate_classifier,
    fit_classifier,
)


DEFAULT_TRAINING_DATA = Path("data/generated/questions_with_answers_training.json")
DEFAULT_VALIDATION_DATA = Path("data/generated/questions_with_answers_validation.json")
DEFAULT_STRUCTURED_DATA = Path("config/data/structured_answer_training_data.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoder", default="models/huggingface/all-MiniLM-L6-v2")
    parser.add_argument("--training-data", type=Path, default=DEFAULT_TRAINING_DATA)
    parser.add_argument("--validation-data", type=Path, default=DEFAULT_VALIDATION_DATA)
    parser.add_argument("--structured-data", type=Path, default=DEFAULT_STRUCTURED_DATA)
    parser.add_argument("--output", type=Path, default=Path("models/answer_semantic_classifier.json"))
    parser.add_argument("--metrics-output", type=Path, default=Path("metrics/semantic_classifier_training.json"))
    parser.add_argument("--min-validation-within-one-accuracy", type=float, default=0.90)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    training_examples = load_answer_regression_examples(args.training_data)
    if args.structured_data.exists():
        training_examples.extend(load_answer_regression_examples(args.structured_data))
    validation_examples = load_answer_regression_examples(args.validation_data)
    encoder = SentenceTransformer(args.encoder, device=args.device)
    extractor = SemanticAnswerFeatureExtractor(encoder)
    training_features = extractor.extract_many([(row.question, row.answer) for row in training_examples])
    validation_features = extractor.extract_many([(row.question, row.answer) for row in validation_examples])
    training_labels = [_letter(row.rating) for row in training_examples]
    validation_labels = [_letter(row.rating) for row in validation_examples]
    classifier = fit_classifier(training_features, training_labels)
    metrics = {
        "model": "semantic_grade_classifier_v1",
        "encoder": args.encoder,
        "training_example_count": len(training_examples),
        "structured_training_data": str(args.structured_data),
        "validation_data": str(args.validation_data),
        "validation": evaluate_classifier(classifier, validation_features, validation_labels),
    }
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    accuracy = float(metrics["validation"]["within_one_letter_accuracy"])
    if accuracy <= args.min_validation_within_one_accuracy:
        raise SystemExit(
            f"Validation within-one-letter accuracy {accuracy:.2%} must be above "
            f"{args.min_validation_within_one_accuracy:.2%}; classifier was not saved."
        )
    classifier.save(args.output)
    print(json.dumps(metrics, indent=2))


def _letter(rating: float) -> str:
    return score_to_letter(round(rating * 100))


if __name__ == "__main__":
    main()
