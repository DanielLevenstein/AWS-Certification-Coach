#!/usr/bin/env python3
"""Compare legacy and v3 answer scorers on one frozen benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aws_certification_coach.model_evaluation.grade_metrics import evaluate_letter_predictions
from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.dataset import load_answer_regression_examples, question_signature
from aws_certification_coach.training.semantic_grade_classifier import (
    SemanticAnswerFeatureExtractor,
    SemanticGradeClassifier,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encoder", default="models/huggingface/all-MiniLM-L6-v2")
    parser.add_argument("--classifier", type=Path, default=Path("models/answer_semantic_classifier.json"))
    parser.add_argument("--benchmark", type=Path, default=Path("data/generated/questions_with_answers_test.json"))
    parser.add_argument("--output", type=Path, default=Path("metrics/answer_evaluator_comparison.json"))
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    examples = load_answer_regression_examples(args.benchmark)
    expected = [score_to_letter(round(example.rating * 100)) for example in examples]
    legacy = [
        score_to_letter(semantic_similarity_score(example.question, example.answer))
        for example in examples
    ]
    encoder = SentenceTransformer(args.encoder, device=args.device)
    extractor = SemanticAnswerFeatureExtractor(encoder)
    features = extractor.extract_many([(example.question, example.answer) for example in examples])
    classifier = SemanticGradeClassifier.load(args.classifier)
    candidate = classifier.predict(features)
    payload = {
        "metrics_schema_version": 3,
        "benchmark": {
            "path": str(args.benchmark),
            "sha256": hashlib.sha256(args.benchmark.read_bytes()).hexdigest(),
            "example_count": len(examples),
            "question_family_count": len({question_signature(example.question) for example in examples}),
            "support_by_grade": {grade: expected.count(grade) for grade in ("A", "B", "C", "D", "F")},
        },
        "evaluators": {
            "legacy_semantic_similarity": evaluate_letter_predictions(expected, legacy),
            "semantic_grade_classifier_v1": evaluate_letter_predictions(expected, candidate),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
