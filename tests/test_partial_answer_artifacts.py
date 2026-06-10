from pathlib import Path

import json

from aws_certification_coach.training.dataset import load_answer_regression_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_generated.json"
HOLDOUT_ARTIFACT = PROJECT_ROOT / "data" / "verification" / "questions_with_answers_holdout.json"


def test_generated_answer_artifact_has_expected_letter_ratings():
    rows = _answer_rows(TRAINING_ARTIFACT)

    assert rows
    assert {row["rating"] for row in rows} == {"A", "B", "C", "D", "F"}
    assert all(isinstance(row["rating"], str) for row in rows)
    assert all("question_id" in row for row in rows)
    assert all("answer" in row for row in rows)

    numeric_examples = load_answer_regression_examples(TRAINING_ARTIFACT)
    assert {example.rating for example in numeric_examples} == {0.95, 0.85, 0.75, 0.65, 0.25}


def test_holdout_graded_answer_artifact_is_separate():
    rows = _answer_rows(HOLDOUT_ARTIFACT)

    assert rows
    assert {row["rating"] for row in rows} == {"A", "B", "C", "D", "F"}
    assert all(row["question_id"].startswith("AWS-HOLDOUT") for row in rows)


def _answer_rows(path: Path) -> list[dict]:
    questions = json.loads(path.read_text(encoding="utf-8"))
    return [
        answer
        for question in questions
        for answer in question.get("generated_answers", [])
    ]
