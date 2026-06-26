"""Grade-band reporting metrics independent of legacy semantic accuracy."""

from __future__ import annotations


class BandAccuracy:
    """Aggregate letter-grade confusion counts into exclusive reporting bands."""

    BANDS = {"A": ("A",), "BC": ("B", "C"), "DF": ("D", "F")}

    def evaluate(
        self,
        confusion: dict[str, dict[str, int]],
    ) -> dict[str, dict[str, float | int | None]]:
        grades = tuple(confusion)
        metrics = {}
        for band, band_grades in self.BANDS.items():
            true_positive = sum(
                confusion[truth][prediction]
                for truth in band_grades
                for prediction in band_grades
            )
            support = sum(
                confusion[truth][prediction]
                for truth in band_grades
                for prediction in grades
            )
            predicted_count = sum(
                confusion[truth][prediction]
                for truth in grades
                for prediction in band_grades
            )
            precision = self._ratio(true_positive, predicted_count)
            recall = self._ratio(true_positive, support)
            metrics[band] = {
                "precision": precision,
                "recall": recall,
                "f1": self._f1(precision, recall),
                "support": support,
            }
        return metrics

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float | None:
        return numerator / denominator if denominator else None

    @staticmethod
    def _f1(precision: float | None, recall: float | None) -> float | None:
        if precision is None or recall is None or precision + recall == 0:
            return None
        return 2 * precision * recall / (precision + recall)
