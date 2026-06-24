import pytest

from aws_certification_coach.model_evaluation.band_accuracy import BandAccuracy

def test_band_accuracy_uses_exclusive_a_bc_df_reporting_contract():
    confusion = {
        "A": {"A": 3, "B": 1, "C": 0, "D": 0, "F": 0},
        "B": {"A": 1, "B": 2, "C": 1, "D": 0, "F": 0},
        "C": {"A": 0, "B": 1, "C": 2, "D": 1, "F": 0},
        "D": {"A": 0, "B": 0, "C": 1, "D": 2, "F": 1},
        "F": {"A": 0, "B": 0, "C": 0, "D": 1, "F": 3},
    }

    metrics = BandAccuracy().evaluate(confusion)

    assert set(metrics) == {"A", "BC", "DF"}
    assert metrics["A"]["support"] == 4
    assert metrics["A"]["precision"] == pytest.approx(3 / 4)
    assert metrics["A"]["recall"] == pytest.approx(3 / 4)
    assert metrics["BC"]["support"] == 8
    assert metrics["BC"]["precision"] == pytest.approx(6 / 8)
    assert metrics["BC"]["recall"] == pytest.approx(6 / 8)
    assert metrics["DF"]["support"] == 8
    assert sum(int(band["support"]) for band in metrics.values()) == sum(
        sum(row.values()) for row in confusion.values()
    )
