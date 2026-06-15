"""Rubric-adherence and held-out model evaluation."""

from __future__ import annotations

import json
from pathlib import Path

from aws_certification_coach.evaluation.factory import build_evaluation_service
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import SemanticAwareEvaluatorProvider
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_grade_band, score_to_letter
from aws_certification_coach.training.answer_classifier import (
    AnswerRegressionModel,
    PartialCreditRegressor,
    evaluate_regression_leave_one_question_out,
)
from aws_certification_coach.training.dataset import (
    load_answer_regression_examples,
    load_feedback_regression_examples,
)


def run_model_evaluation(
    training_questions_path: Path,
    app_questions_path: Path,
    training_path: Path,
    curated_path: Path,
    epochs: int = 500,
    learning_rate: float = 0.02,
) -> dict[str, object]:
    training_questions = JsonQuestionRepository(training_questions_path).all()
    training_questions_by_id = {question.question_id: question for question in training_questions}
    app_questions = JsonQuestionRepository(app_questions_path).all()
    app_questions_by_id = {question.question_id: question for question in app_questions}
    training_examples = load_answer_regression_examples(training_path)
    held_out = evaluate_regression_leave_one_question_out(
        PartialCreditRegressor(epochs=epochs, learning_rate=learning_rate, seed=0),
        training_questions_by_id,
        training_examples,
    )
    rubric = evaluate_curated_answers(curated_path, app_questions_by_id)
    return {
        "held_out_performance": held_out,
        "rubric_adherence": rubric,
    }


def evaluate_curated_answers(
    curated_path: Path,
    questions_by_id: dict,
) -> dict[str, object]:
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    examples = load_feedback_regression_examples(curated_path, questions_by_id)
    service = build_evaluation_service()
    mismatches = []
    matches = 0
    for index, (row, example) in enumerate(zip(rows, examples, strict=True)):
        result = service.evaluate(questions_by_id[example.question_id], example.answer)
        expected = str(row["correct_rating"]).strip().upper()
        actual = score_to_letter(result.score)
        expected_band = letter_to_grade_band(expected)
        actual_band = letter_to_grade_band(actual)
        if actual_band == expected_band:
            matches += 1
            continue
        mismatches.append(
            {
                "row": index,
                "question_id": example.question_id,
                "answer": example.answer,
                "expected": expected,
                "actual": actual,
                "expected_band": expected_band,
                "actual_band": actual_band,
                "score": result.score,
            }
        )
    total = len(examples)
    return {
        "example_count": total,
        "matching_grade_bands": matches,
        "grade_accuracy": matches / max(1, total),
        "grade_bands": ["A/B", "C/D", "F"],
        "mismatches": mismatches,
    }


def evaluate_curated_model(
    model: AnswerRegressionModel,
    curated_path: Path,
    questions_by_id: dict,
) -> dict[str, float]:
    del model
    rows = json.loads(curated_path.read_text(encoding="utf-8"))
    examples = load_feedback_regression_examples(curated_path, questions_by_id)
    service = EvaluationService(SemanticAwareEvaluatorProvider())
    matches = 0
    for row, example in zip(rows, examples, strict=True):
        result = service.evaluate(questions_by_id[example.question_id], example.answer)
        actual = score_to_letter(result.score)
        expected = str(row["correct_rating"]).strip().upper()
        matches += int(letter_to_grade_band(actual) == letter_to_grade_band(expected))
    return {
        "curated_grade_accuracy": matches / max(1, len(examples)),
        "curated_example_count": len(examples),
    }
