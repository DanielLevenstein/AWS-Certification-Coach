import json

from aws_certification_coach.domain import Question
from aws_certification_coach.training.answer_classifier import AnswerRegressionModel, PartialCreditRegressor
from aws_certification_coach.training.dataset import AnswerRegressionExample
from scripts.evaluate_answer_model import evaluate_model_splits, render_markdown_table


def test_regressor_records_metrics_at_requested_training_checkpoints():
    question = Question(
        certification="Test",
        domain="Test",
        difficulty="Easy",
        question="Name the service.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
    )
    examples = [
        AnswerRegressionExample(question, "Use AWS KMS.", 0.95),
        AnswerRegressionExample(question, "AWS", 0.25),
    ]

    model, history = PartialCreditRegressor(epochs=5, seed=0).train_with_history(
        [question],
        examples,
        checkpoints=[1, 3, 5],
        checkpoint_evaluator=lambda _model: {"curated_grade_accuracy": 0.5},
    )

    assert [point["epoch"] for point in history] == [1, 3, 5]
    assert all(point["example_count"] == 2 for point in history)
    assert all(point["curated_grade_accuracy"] == 0.5 for point in history)
    assert model.feature_names


def test_evaluate_answer_model_splits_reports_each_split(tmp_path):
    question = Question(
        certification="Test",
        domain="Test",
        difficulty="Easy",
        question="Name the service.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
    )
    row = {
        "certification": question.certification,
        "domain": question.domain,
        "difficulty": question.difficulty,
        "question": question.question,
        "reference_answer": question.reference_answer,
        "key_concepts": question.key_concepts,
        "partial_answers": [
            {"answer": "Use AWS KMS.", "rating": 0.95},
            {"answer": "Use Amazon S3.", "rating": 0.25},
        ],
    }
    split_paths = {}
    for split in ("train", "validation", "test"):
        path = tmp_path / f"{split}.json"
        path.write_text(f"[{json.dumps(row)}]\n", encoding="utf-8")
        split_paths[split] = path
    model = AnswerRegressionModel(
        feature_names=["bias"],
        weights=[0.95],
        answer_form="long",
    )

    report = evaluate_model_splits(model, split_paths)

    assert report["model"]["feature_mismatch"] is True
    assert set(report["splits"]) == {"train", "validation", "test"}
    assert report["splits"]["train"]["example_count"] == 2
    assert "letter_accuracy" in report["splits"]["validation"]
    assert "letter_confusion" in report["splits"]["test"]
    assert set(report["splits"]["test"]["per_grade"]) == {"A", "B", "C", "D", "F"}
    assert report["splits"]["test"]["per_grade"]["A"] == {
        "precision": 0.5,
        "recall": 1.0,
        "f1": 2 / 3,
        "support": 1,
    }

    table = render_markdown_table(report)

    assert "| Split | Examples | Within 1 Letter | Exact Letter | MAE | MSE |" in table
    assert "| Train | 2 |" in table
    assert "50.0%" in table
