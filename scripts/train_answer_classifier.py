"""Train and evaluate the answer classification model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.answer_classifier import (
    ReinforcementAnswerClassifier,
    evaluate_leave_one_question_out,
    evaluate_model,
)
from aws_certification_coach.training.dataset import (
    load_answer_classification_examples,
    load_feedback_classification_examples,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default="data/generated/questions_with_answers_generated.json")
    parser.add_argument("--training-data", default="data/generated/questions_with_answers_generated.json")
    parser.add_argument(
        "--feedback-data",
        action="append",
        default=["data/curated/curated_training_data.json", "data/generated/user_feedback.json"],
    )
    parser.add_argument("--output", default="models/answer_classifier.json")
    parser.add_argument("--metrics-output", default="models/answer_classifier_metrics.json")
    parser.add_argument("--min-accuracy", type=float, default=0.90)
    parser.add_argument("--max-accuracy", type=float, default=0.999)
    parser.add_argument("--min-examples", type=int, default=50)
    parser.add_argument("--eval-mode", choices=["leave-one-question-out", "training"], default="leave-one-question-out")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--learning-rate", type=float, default=0.08)
    args = parser.parse_args()

    questions = JsonQuestionRepository(args.questions).all()
    questions_by_id = {question.question_id: question for question in questions}
    examples = load_answer_classification_examples(args.training_data)
    for feedback_path in args.feedback_data:
        if Path(feedback_path).exists():
            examples.extend(load_feedback_classification_examples(feedback_path, questions_by_id))
    _validate_examples(questions_by_id, examples)
    if len(examples) < args.min_examples:
        raise SystemExit(
            f"Only {len(examples)} training examples are available. "
            f"Refusing to certify model performance with fewer than {args.min_examples} examples."
        )

    trainer = ReinforcementAnswerClassifier(
        learning_rate=args.learning_rate,
        epochs=args.epochs,
    )
    if args.eval_mode == "leave-one-question-out":
        metrics = evaluate_leave_one_question_out(trainer, questions_by_id, examples)
    else:
        model_for_training_metrics = trainer.train(questions_by_id, examples)
        metrics = evaluate_model(model_for_training_metrics, questions_by_id, examples)

    metrics["eval_mode"] = args.eval_mode
    metrics["example_count"] = len(examples)
    metrics["min_examples"] = args.min_examples
    metrics["min_accuracy"] = args.min_accuracy
    metrics["max_accuracy"] = args.max_accuracy

    if metrics["accuracy"] < args.min_accuracy:
        _write_metrics(args.metrics_output, metrics)
        raise SystemExit(
            f"Held-out model accuracy {metrics['accuracy']:.3f} is below required {args.min_accuracy:.3f}."
        )
    if metrics["accuracy"] >= args.max_accuracy:
        metrics["suspicious_accuracy"] = True
        _write_metrics(args.metrics_output, metrics)
        raise SystemExit(
            f"Held-out model accuracy {metrics['accuracy']:.3f} is suspiciously high. "
            "Regenerate harder examples before treating this as deployable."
        )
    metrics["suspicious_accuracy"] = False

    model = trainer.train(questions_by_id, examples)
    model.save(args.output)
    _write_metrics(args.metrics_output, metrics)
    print(json.dumps(metrics, indent=2))


def _write_metrics(metrics_output: str, metrics: dict[str, float]) -> None:
    metrics_path = Path(metrics_output)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")


def _validate_examples(questions_by_id, examples) -> None:
    missing = sorted({example.question_id for example in examples if example.question_id not in questions_by_id})
    if missing:
        raise ValueError(f"Training examples reference unknown question IDs: {', '.join(missing)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Training failed: {exc}", file=sys.stderr)
        raise
