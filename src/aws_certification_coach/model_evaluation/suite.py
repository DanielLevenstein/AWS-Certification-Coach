"""Rubric-adherence and held-out model evaluation."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import TrainedRegressionEvaluatorProvider
from aws_certification_coach.model_evaluation.semantic_similarity import evaluate_semantic_curated_answers
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_numeric, score_to_letter
from aws_certification_coach.training.answer_classifier import (
    AnswerRegressionModel,
    PartialCreditRegressor,
    evaluate_regression_leave_one_question_out,
)
from aws_certification_coach.training.dataset import (
    load_answer_regression_examples,
    load_feedback_regression_examples,
)
from aws_certification_coach.training.features import correct_answer_text


def run_model_evaluation(
    training_questions_path: Path,
    app_questions_path: Path,
    training_path: Path,
    curated_path: Path | Iterable[Path],
    epochs: int = 500,
    learning_rate: float = 0.02,
) -> dict[str, object]:
    training_questions = JsonQuestionRepository(training_questions_path).all()
    app_questions = JsonQuestionRepository(app_questions_path).all()
    training_examples = load_answer_regression_examples(training_path)
    held_out = evaluate_regression_leave_one_question_out(
        PartialCreditRegressor(epochs=epochs, learning_rate=learning_rate, seed=0),
        training_questions,
        training_examples,
    )
    rubric = evaluate_curated_answers(curated_path, app_questions)
    semantic = evaluate_semantic_curated_answers(curated_path, app_questions)
    return {
        "held_out_performance": held_out,
        "rubric_adherence": rubric,
        "semantic_similarity": semantic,
    }


def evaluate_curated_answers(
    curated_path: Path | Iterable[Path],
    questions: list,
) -> dict[str, object]:
    service = build_evaluation_service()
    mismatches = []
    matches = 0
    rows_and_examples = _feedback_rows_and_examples(curated_path, questions)
    for index, (source_path, source_row, row, example) in enumerate(rows_and_examples):
        result = service.evaluate(example.question, example.answer)
        expected = str(row["correct_rating"]).strip().upper()
        actual = score_to_letter(result.score)
        if actual == expected:
            matches += 1
            continue
        mismatches.append(
            {
                "row": index,
                "source": str(source_path),
                "source_row": source_row,
                "question": example.question.question,
                "user_answer": example.answer,
                "correct_answer": correct_answer_text(example.question),
                "expected_rating": letter_to_numeric(expected),
                "expected_letter": expected,
                "actual_letter": actual,
                "score": result.score,
            }
        )
    total = len(rows_and_examples)
    return {
        "example_count": total,
        "matching_letter_grades": matches,
        "grade_accuracy": matches / max(1, total),
        "grade_scale": ["A", "B", "C", "D", "F"],
        "mismatches": mismatches,
    }


def evaluate_curated_model(
    model: AnswerRegressionModel,
    curated_path: Path | Iterable[Path],
    questions: list,
) -> dict[str, float]:
    service = EvaluationService(TrainedRegressionEvaluatorProvider(model))
    matches = 0
    rows_and_examples = _feedback_rows_and_examples(curated_path, questions)
    for _source_path, _source_row, row, example in rows_and_examples:
        result = service.evaluate(example.question, example.answer)
        actual = score_to_letter(result.score)
        expected = str(row["correct_rating"]).strip().upper()
        matches += int(actual == expected)
    return {
        "curated_grade_accuracy": matches / max(1, len(rows_and_examples)),
        "curated_example_count": len(rows_and_examples),
    }


def _feedback_rows_and_examples(
    curated_path: Path | Iterable[Path],
    questions: list,
) -> list[tuple[Path, int, dict, object]]:
    paths = [curated_path] if isinstance(curated_path, Path) else list(curated_path)
    rows_and_examples = []
    for path in paths:
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            raise ValueError(f"Curated feedback must be a JSON list: {path}")
        examples = load_feedback_regression_examples(path, questions)
        rows_and_examples.extend(
            (path, row_index, row, example)
            for row_index, (row, example) in enumerate(zip(rows, examples, strict=True))
            if isinstance(row, dict)
        )
    return rows_and_examples
