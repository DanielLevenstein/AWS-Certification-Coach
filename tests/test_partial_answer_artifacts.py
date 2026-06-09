from pathlib import Path

import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_PARTIAL_ARTIFACT = PROJECT_ROOT / "data" / "training" / "partial_answer_ratings_generated.json"
HOLDOUT_PARTIAL_ARTIFACT = PROJECT_ROOT / "data" / "verification" / "answers" / "partial_answer_ratings_holdout.json"


def test_partial_answer_artifact_has_expected_ratings():
    rows = json.loads(TRAINING_PARTIAL_ARTIFACT.read_text(encoding="utf-8"))

    assert rows
    assert {row["rating_bucket"] for row in rows} == {0.25, 0.50, 0.75}
    assert all(0 <= row["rating"] <= 1 for row in rows)
    assert len({row["rating"] for row in rows}) > 3
    assert all("question_id" in row for row in rows)
    assert all("answer" in row for row in rows)


def test_holdout_partial_answer_artifact_is_separate():
    rows = json.loads(HOLDOUT_PARTIAL_ARTIFACT.read_text(encoding="utf-8"))

    assert rows
    assert {row["rating_bucket"] for row in rows} == {0.25, 0.50, 0.75}
    assert all(row["question_id"].startswith("AWS-HOLDOUT") for row in rows)
