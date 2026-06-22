"""Shared legacy-compatible and five-class learner-grade metrics."""

from __future__ import annotations


GRADES = ("A", "B", "C", "D", "F")
GRADE_INDEX = {grade: index for index, grade in enumerate(GRADES)}
GRADE_BAND = {"A": "A/B", "B": "A/B", "C": "C/D", "D": "C/D", "F": "F"}


def evaluate_letter_predictions(expected: list[str], predicted: list[str]) -> dict[str, object]:
    if not expected or len(expected) != len(predicted):
        raise ValueError("Expected and predicted grades must be non-empty and have equal length.")
    unknown = sorted((set(expected) | set(predicted)) - set(GRADES))
    if unknown:
        raise ValueError(f"Unsupported grades: {', '.join(unknown)}")

    confusion = {grade: {candidate: 0 for candidate in GRADES} for grade in GRADES}
    exact = band_matches = within_one = severe = 0
    ordinal_error = 0
    accepted_tp = accepted_fp = accepted_fn = 0
    for truth, prediction in zip(expected, predicted, strict=True):
        confusion[truth][prediction] += 1
        distance = abs(GRADE_INDEX[truth] - GRADE_INDEX[prediction])
        exact += int(truth == prediction)
        band_matches += int(GRADE_BAND[truth] == GRADE_BAND[prediction])
        within_one += int(distance <= 1)
        severe += int(distance >= 2)
        ordinal_error += distance
        expected_accepted = truth != "F"
        predicted_accepted = prediction != "F"
        accepted_tp += int(expected_accepted and predicted_accepted)
        accepted_fp += int(not expected_accepted and predicted_accepted)
        accepted_fn += int(expected_accepted and not predicted_accepted)

    per_grade = {}
    for grade in GRADES:
        true_positive = confusion[grade][grade]
        support = sum(confusion[grade].values())
        predicted_count = sum(confusion[truth][grade] for truth in GRADES)
        precision = _ratio(true_positive, predicted_count)
        recall = _ratio(true_positive, support)
        f1 = _f1(precision, recall)
        per_grade[grade] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
        }

    total = len(expected)
    macro_precision = _macro(per_grade, "precision")
    macro_recall = _macro(per_grade, "recall")
    macro_f1 = _macro(per_grade, "f1")
    grade_band_accuracy = band_matches / total
    return {
        "example_count": total,
        "grade_band_accuracy": grade_band_accuracy,
        "semantic_accuracy": grade_band_accuracy,
        "semantic_precision": _ratio(accepted_tp, accepted_tp + accepted_fp),
        "semantic_recall": _ratio(accepted_tp, accepted_tp + accepted_fn),
        "exact_letter_accuracy": exact / total,
        "within_one_letter_accuracy": within_one / total,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "ordinal_mae": ordinal_error / total,
        "severe_error_rate": severe / total,
        "f_rejection_recall": per_grade["F"]["recall"],
        "per_grade": per_grade,
        "confusion_matrix": confusion,
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _f1(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None or precision + recall == 0:
        return None
    return 2 * precision * recall / (precision + recall)


def _macro(per_grade: dict[str, dict[str, float | int | None]], key: str) -> float | None:
    values = [per_grade[grade][key] for grade in GRADES]
    if any(value is None for value in values):
        return None
    return sum(float(value) for value in values) / len(values)
