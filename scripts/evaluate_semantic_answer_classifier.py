#!/usr/bin/env python3
"""Final-report evaluation for the saved local semantic grade classifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.dataset import load_answer_regression_examples
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
    parser.add_argument("--device", default=None)
    parser.add_argument("--min-test-accuracy", type=float, default=0.80)
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    examples = load_answer_regression_examples(args.test_data)
    encoder = SentenceTransformer(args.encoder, device=args.device)
    extractor = SemanticAnswerFeatureExtractor(encoder)
    features = extractor.extract_many([(row.question, row.answer) for row in examples])
    labels = [score_to_letter(round(row.rating * 100)) for row in examples]
    classifier = SemanticGradeClassifier.load(args.classifier)
    metrics = {
        "model": "semantic_grade_classifier_v1",
        "test_data": str(args.test_data),
        "test": evaluate_classifier(classifier, features, labels),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    accuracy = float(metrics["test"]["exact_letter_accuracy"])
    if accuracy < args.min_test_accuracy:
        raise SystemExit(
            f"Final test exact-letter accuracy {accuracy:.2%} is below "
            f"{args.min_test_accuracy:.2%}."
        )


if __name__ == "__main__":
    main()
