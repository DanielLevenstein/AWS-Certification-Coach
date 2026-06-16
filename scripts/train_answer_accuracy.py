"""Train and evaluate the partial-credit answer regression model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.model_evaluation.suite import evaluate_curated_model
from aws_certification_coach.training.answer_classifier import (
    PartialCreditRegressor,
    evaluate_regression_leave_one_question_out,
    evaluate_regression_model,
)
from aws_certification_coach.training.dataset import load_answer_regression_examples, load_feedback_regression_examples


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="data/generated/questions_with_answers_generated.json")
    parser.add_argument("--training-data", default="data/generated/questions_with_answers_generated.json")
    parser.add_argument("--app-questions", default="data/questions/sample_questions.json")
    parser.add_argument("--curated-data", default="data/curated/curated_training_data.json")
    parser.add_argument(
        "--feedback-data",
        action="append",
        default=[
            "data/curated/curated_training_data.json",
            "data/curated/curated_training_data2.json",
            "data/generated/user_feedback.v1.json",
        ],
    )
    parser.add_argument("--output", default="models/answer_regressor_model.json")
    parser.add_argument("--metrics-output", default="models/answer_regressor_model_metrics.json")
    parser.add_argument("--history-output", default="release/metrics/training_history.json")
    parser.add_argument("--max-mse", type=float, default=0.06)
    parser.add_argument("--min-examples", type=int, default=100)
    parser.add_argument("--eval-mode", choices=["leave-one-question-out", "training"], default="leave-one-question-out")
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--learning-rate", type=float, default=0.02)
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    examples = load_answer_regression_examples(args.training_data)
    app_questions = JsonQuestionRepository(args.app_questions).all()
    feedback_questions = questions + app_questions
    for feedback_path in args.feedback_data:
        if Path(feedback_path).exists():
            examples.extend(load_feedback_regression_examples(feedback_path, feedback_questions))
    if len(examples) < args.min_examples:
        raise SystemExit(
            f"Only {len(examples)} partial-credit examples are available. "
            f"Refusing to certify regression performance with fewer than {args.min_examples} examples."
        )

    trainer = PartialCreditRegressor(learning_rate=args.learning_rate, epochs=args.epochs, seed=0)
    if args.eval_mode == "leave-one-question-out":
        metrics = evaluate_regression_leave_one_question_out(trainer, questions, examples)
    else:
        model_for_training_metrics = trainer.train(questions, examples)
        metrics = evaluate_regression_model(model_for_training_metrics, questions, examples)

    metrics["eval_mode"] = args.eval_mode
    metrics["min_examples"] = args.min_examples
    metrics["max_mse"] = args.max_mse

    if metrics["mse"] > args.max_mse:
        _write_metrics(args.metrics_output, metrics)
        raise SystemExit(f"Held-out partial-credit MSE {metrics['mse']:.3f} exceeds required {args.max_mse:.3f}.")

    model, history = trainer.train_with_history(
        questions,
        examples,
        checkpoint_evaluator=lambda checkpoint_model: evaluate_curated_model(
            checkpoint_model,
            Path(args.curated_data),
            app_questions,
        ),
    )
    model.save(args.output)
    _write_metrics(args.history_output, {"checkpoints": history})
    _write_metrics(args.metrics_output, metrics)
    print(json.dumps(metrics, indent=2))


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
