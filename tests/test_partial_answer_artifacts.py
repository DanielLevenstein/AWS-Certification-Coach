from pathlib import Path

import json

from aws_certification_coach.training.dataset import load_answer_regression_examples


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_training.json"
VALIDATION_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_validation.json"
TEST_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"


def test_generated_answer_artifact_has_expected_letter_ratings():
    rows = _answer_rows(TRAINING_ARTIFACT)

    assert rows
    assert {row["rating"] for row in rows} == {"A", "B", "C", "D", "F"}
    assert all(isinstance(row["rating"], str) for row in rows)
    assert {row["intended_coverage"] for row in rows} == {1.0, 0.85, 0.75, 0.5, 0.25, 0.0}
    assert all("answer" in row for row in rows)

    numeric_examples = load_answer_regression_examples(TRAINING_ARTIFACT)
    assert {example.rating for example in numeric_examples} == {0.95, 0.85, 0.75, 0.65, 0.25}


def test_validation_and_test_answer_artifacts_are_separate():
    training_questions = _questions(TRAINING_ARTIFACT)
    validation_questions = _questions(VALIDATION_ARTIFACT)
    test_questions = _questions(TEST_ARTIFACT)
    rows = _answer_rows(TEST_ARTIFACT)

    assert rows
    assert {row["rating"] for row in rows} == {"A", "B", "C", "D", "F"}
    assert all("answer" in row for row in rows)
    assert _question_texts(training_questions).isdisjoint(_question_texts(validation_questions))
    assert _question_texts(training_questions).isdisjoint(_question_texts(test_questions))
    assert _question_texts(validation_questions).isdisjoint(_question_texts(test_questions))


def _answer_rows(path: Path) -> list[dict]:
    return [
        answer
        for question in _questions(path)
        for answer in question.get("generated_answers", [])
    ]


def _questions(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _question_texts(questions: list[dict]) -> set[str]:
    return {str(question["question"]) for question in questions}
