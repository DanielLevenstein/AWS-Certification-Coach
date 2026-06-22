import numpy as np

from aws_certification_coach.training.semantic_grade_classifier import (
    FEATURE_VERSION,
    SemanticGradeClassifier,
    evaluate_classifier,
)
from scripts import train_semantic_answer_classifier


def test_semantic_classifier_round_trips_json(tmp_path):
    model = SemanticGradeClassifier(
        classes=["A", "F"],
        coefficients=[[1.0, 0.0], [-1.0, 0.0]],
        intercepts=[0.0, 0.0],
        means=[0.0, 0.0],
        scales=[1.0, 1.0],
    )
    path = tmp_path / "classifier.json"

    model.save(path)
    loaded = SemanticGradeClassifier.load(path)

    assert loaded.feature_version == FEATURE_VERSION
    assert loaded.predict(np.asarray([[1.0, 0.0], [-1.0, 0.0]])) == ["A", "F"]


def test_semantic_classifier_reports_exact_letter_accuracy():
    model = SemanticGradeClassifier(
        classes=["A", "F"],
        coefficients=[[1.0], [-1.0]],
        intercepts=[0.0, 0.0],
        means=[0.0],
        scales=[1.0],
    )

    metrics = evaluate_classifier(model, np.asarray([[1.0], [-1.0]]), ["A", "F"])

    assert metrics["exact_letter_accuracy"] == 1


def test_training_defaults_never_use_final_test_data():
    assert "test" not in train_semantic_answer_classifier.DEFAULT_TRAINING_DATA.name
    assert "test" not in train_semantic_answer_classifier.DEFAULT_VALIDATION_DATA.name


def test_final_evaluation_uses_only_the_test_split():
    from scripts import evaluate_semantic_answer_classifier

    assert "test" in evaluate_semantic_answer_classifier.DEFAULT_TEST_DATA.name
