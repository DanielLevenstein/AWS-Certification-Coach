#!/usr/bin/env python3
"""Evaluate curated answers with deterministic semantic-aware scoring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.model_evaluation.semantic_similarity import (
    evaluate_semantic_curated_answers,
)
from aws_certification_coach.questions.json_repository import JsonQuestionRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated/curated_training_data.json"))
    parser.add_argument("--questions", type=Path, default=Path("data/questions/sample_questions.json"))
    parser.add_argument("--output", type=Path, default=Path("release/metrics/semantic_similarity.json"))
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    questions_by_id = {question.question_id: question for question in questions}
    metrics = evaluate_semantic_curated_answers(args.curated, questions_by_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
