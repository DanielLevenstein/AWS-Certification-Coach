import pytest

from aws_certification_coach.model_evaluation.grade_metrics import (
    evaluate_letter_predictions,
    evaluate_release_gates,
)


def test_semantic_metrics_treat_a_through_c_as_accepted():
    metrics = evaluate_letter_predictions(
        ["A", "B", "C", "D", "F"],
        ["B", "C", "D", "F", "A"],
    )

    assert metrics["grade_band_accuracy"] == pytest.approx(2 / 5)
    assert metrics["semantic_accuracy"] == metrics["grade_band_accuracy"]
    assert metrics["semantic_precision"] == pytest.approx(2 / 3)
    assert metrics["semantic_recall"] == pytest.approx(2 / 3)
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


def test_perfect_five_grade_results_pass_frozen_release_gates():
    metrics = evaluate_letter_predictions(
        ["A", "B", "C", "D", "F"],
        ["A", "B", "C", "D", "F"],
    )

    gates = evaluate_release_gates(metrics)

    assert gates["passed"] is True
    assert gates["failures"] == []
    assert gates["thresholds"]["within_one_letter_accuracy"] == {
        "minimum_exclusive": 0.90
    }


def test_release_gates_require_support_and_recall_for_every_grade():
    metrics = evaluate_letter_predictions(["A", "B", "C", "D"], ["A", "B", "C", "D"])

    gates = evaluate_release_gates(metrics)

    assert gates["passed"] is False
    assert "F has no benchmark support" in gates["failures"]


def test_release_gate_requires_more_than_ninety_percent_within_one_letter():
    metrics = evaluate_letter_predictions(
        ["A"] * 10,
        ["A"] * 9 + ["C"],
    )
    metrics["per_grade"] = {
        grade: {"support": 1, "recall": 1.0} for grade in ("A", "B", "C", "D", "F")
    }

    gates = evaluate_release_gates(metrics)

    assert metrics["within_one_letter_accuracy"] == 0.9
    assert gates["passed"] is False
    assert gates["failures"] == [
        "within_one_letter_accuracy 90.00% must be above 90.00%"
    ]
