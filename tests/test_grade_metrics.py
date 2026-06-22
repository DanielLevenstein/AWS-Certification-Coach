import pytest

from aws_certification_coach.model_evaluation.grade_metrics import evaluate_letter_predictions


def test_legacy_compatible_grade_metrics_keep_original_definitions():
    metrics = evaluate_letter_predictions(
        ["A", "B", "C", "D", "F"],
        ["B", "C", "D", "F", "A"],
    )

    assert metrics["grade_band_accuracy"] == pytest.approx(2 / 5)
    assert metrics["semantic_accuracy"] == metrics["grade_band_accuracy"]
    assert metrics["semantic_precision"] == pytest.approx(3 / 4)
    assert metrics["semantic_recall"] == pytest.approx(3 / 4)
    assert metrics["exact_letter_accuracy"] == 0
    assert metrics["within_one_letter_accuracy"] == pytest.approx(4 / 5)


def test_five_class_metrics_report_per_grade_and_ordinal_errors():
    metrics = evaluate_letter_predictions(
        ["A", "B", "C", "D", "F"],
        ["A", "B", "C", "D", "F"],
    )

    assert metrics["macro_precision"] == 1
    assert metrics["macro_recall"] == 1
    assert metrics["macro_f1"] == 1
    assert metrics["ordinal_mae"] == 0
    assert metrics["severe_error_rate"] == 0
    assert metrics["f_rejection_recall"] == 1
    assert set(metrics["per_grade"]) == {"A", "B", "C", "D", "F"}
    assert metrics["confusion_matrix"]["A"]["A"] == 1


def test_grade_metrics_reject_empty_or_unknown_inputs():
    with pytest.raises(ValueError):
        evaluate_letter_predictions([], [])
    with pytest.raises(ValueError):
        evaluate_letter_predictions(["A"], ["E"])
