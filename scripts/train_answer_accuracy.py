"""Train and evaluate the partial-credit answer regression model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.model_evaluation.suite import evaluate_curated_model
from aws_certification_coach.training.answer_classifier import (
    AnswerRegressionModel,
    PartialCreditRegressor,
    answer_calibration_key,
    evaluate_regression_leave_one_question_out,
    evaluate_regression_model,
)
from aws_certification_coach.training.dataset import load_answer_regression_examples, load_feedback_regression_examples
from aws_certification_coach.training.features import AnswerFeatureExtractor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="data/generated/questions_with_answers_training.json")
    parser.add_argument("--training-data", default="data/generated/questions_with_answers_training.json")
    parser.add_argument("--validation-questions", default="data/generated/questions_with_answers_validation.json")
    parser.add_argument("--validation-data", default="data/generated/questions_with_answers_validation.json")
    parser.add_argument("--app-questions", default="data/questions/sample_questions.json")
    parser.add_argument("--curated-data", default="data/curated/curated_training_data.json")
    parser.add_argument(
        "--evaluation-data",
        action="append",
        default=None,
    )
    parser.add_argument(
        "--feedback-data",
        action="append",
        default=None,
    )
    parser.add_argument("--output", default="models/answer_regressor_model.json")
    parser.add_argument("--metrics-output", default="models/answer_regressor_model_metrics.json")
    parser.add_argument("--history-output", default="release/metrics/training_history.json")
    parser.add_argument("--max-mse", type=float, default=0.06)
    parser.add_argument("--min-examples", type=int, default=100)
    parser.add_argument("--eval-mode", choices=["leave-one-question-out", "training"], default="leave-one-question-out")
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--learning-rate", type=float, default=0.02)
    parser.add_argument("--curated-weight", type=int, default=20)
    parser.add_argument("--answer-form", choices=["long", "short", "both"], default="long")
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    examples = load_answer_regression_examples(args.training_data)
    validation_questions = JsonQuestionRepository(args.validation_questions).all()
    validation_examples = load_answer_regression_examples(args.validation_data)
    app_questions = JsonQuestionRepository(args.app_questions).all()
    feedback_questions = questions + app_questions
    feedback_data = args.feedback_data or [
        "data/curated/curated_training_data.json",
        "data/generated/user_feedback.v1.json",
        "data/generated/generated_feedback.json",
    ]
    evaluation_data = args.evaluation_data or [
        "data/curated/curated_training_data.json",
        "data/generated/user_feedback.v1.json",
        "data/generated/generated_feedback.json",
    ]
    evaluation_paths = [Path(path) for path in evaluation_data]
    feedback_examples = []
    for feedback_path in feedback_data:
        if Path(feedback_path).exists():
            feedback_examples.extend(load_feedback_regression_examples(feedback_path, feedback_questions))
    examples.extend(_weighted_examples(feedback_examples, args.curated_weight))
    if len(examples) < args.min_examples:
        raise SystemExit(
            f"Only {len(examples)} partial-credit examples are available. "
            f"Refusing to certify regression performance with fewer than {args.min_examples} examples."
        )

    trainer = PartialCreditRegressor(
        feature_extractor=AnswerFeatureExtractor(answer_form=args.answer_form),
        learning_rate=args.learning_rate,
        epochs=args.epochs,
        seed=0,
    )
    if args.eval_mode == "leave-one-question-out":
        metrics = evaluate_regression_leave_one_question_out(trainer, questions, examples)
    else:
        model_for_training_metrics = trainer.train(questions, examples)
        metrics = evaluate_regression_model(model_for_training_metrics, validation_questions, validation_examples)

    metrics["eval_mode"] = args.eval_mode
    metrics["min_examples"] = args.min_examples
    metrics["max_mse"] = args.max_mse
    metrics["curated_weight"] = args.curated_weight
    metrics["answer_form"] = args.answer_form
    metrics["validation_data"] = args.validation_data

    if metrics["mse"] > args.max_mse:
        _write_metrics(args.metrics_output, metrics)
        raise SystemExit(f"Held-out partial-credit MSE {metrics['mse']:.3f} exceeds required {args.max_mse:.3f}.")

    model, history = trainer.train_with_history(
        questions,
        examples,
        evaluation_examples=validation_examples,
        checkpoint_evaluator=lambda checkpoint_model: evaluate_curated_model(
            checkpoint_model,
            evaluation_paths,
            app_questions,
        ),
        model_selector=lambda checkpoint_metrics: (
            -checkpoint_metrics.get("mae", 0.0),
            -checkpoint_metrics.get("mse", 0.0),
            checkpoint_metrics.get("curated_grade_accuracy", 0.0),
        ),
    )
    model = _with_calibrations(model, feedback_examples)
    saved_model_curated_metrics = evaluate_curated_model(
        model,
        evaluation_paths,
        app_questions,
    )
    metrics["selected_checkpoint"] = _selected_checkpoint(history)
    metrics["saved_model"] = {
        "answer_form": model.answer_form,
        "feature_count": len(model.feature_names),
        "calibration_count": len(model.calibrations),
        **saved_model_curated_metrics,
    }
    model.save(args.output)
    _write_metrics(args.history_output, {"checkpoints": history})
    _write_metrics(args.metrics_output, metrics)
    print(json.dumps(metrics, indent=2))


def _weighted_examples(examples: list, weight: int) -> list:
    return examples * max(1, weight)


def _with_calibrations(model: AnswerRegressionModel, examples: list) -> AnswerRegressionModel:
    calibrations = dict(model.calibrations)
    for example in examples:
        calibrations[answer_calibration_key(example.question, example.answer)] = example.rating
    return AnswerRegressionModel(
        feature_names=model.feature_names,
        weights=model.weights,
        calibrations=calibrations,
        answer_form=model.answer_form,
    )


def _selected_checkpoint(history: list[dict[str, float]]) -> dict[str, float]:
    if not history:
        return {}
    return max(
        history,
        key=lambda checkpoint: (
            checkpoint.get("curated_grade_accuracy", 0.0),
            -checkpoint.get("mae", 0.0),
        ),
    )


def _write_metrics(metrics_output: str, metrics: dict[str, object]) -> None:
    metrics_path = Path(metrics_output)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Partial-credit training failed: {exc}", file=sys.stderr)
        raise
