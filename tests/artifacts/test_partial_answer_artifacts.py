from pathlib import Path

import json

from aws_certification_coach.training.dataset import (
    load_answer_regression_examples,
    load_curated_question_regression_examples,
    load_curated_structured_regression_examples,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_training.json"
VALIDATION_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_validation.json"
TEST_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "questions_with_answers_test.json"
EXACT_GRADE_ARTIFACT = PROJECT_ROOT / "data" / "generated" / "exact_letter_grade_answer_examples.json"
STRUCTURED_TRAINING_ARTIFACT = PROJECT_ROOT / "config" / "data" / "structured_answer_training_data.json"
CURATED_STRUCTURED_TRAINING_ARTIFACT = PROJECT_ROOT / "data" / "curated" / "structured_answer_training_data.json"


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


def test_exact_letter_grade_dataset_is_clean_and_held_out():
    examples = json.loads(EXACT_GRADE_ARTIFACT.read_text(encoding="utf-8"))
    training_questions = _questions(TRAINING_ARTIFACT)

    assert examples
    assert {example["expected_letter_grade"] for example in examples} == {"A", "B", "C", "D", "F"}
    assert all(example["question_type"] == "service_selection" for example in examples)
    assert all(example["required_concepts"] for example in examples)
    assert all(example["acceptable_answers"] for example in examples)
    assert _question_texts(training_questions).isdisjoint({str(example["question"]) for example in examples})


def test_structured_answer_training_data_uses_partial_answer_schema():
    examples = json.loads(STRUCTURED_TRAINING_ARTIFACT.read_text(encoding="utf-8"))
    numeric_examples = load_answer_regression_examples(STRUCTURED_TRAINING_ARTIFACT)
    curated_examples = load_curated_structured_regression_examples(CURATED_STRUCTURED_TRAINING_ARTIFACT)

    assert examples
    assert numeric_examples
    assert curated_examples
    assert all(question["partial_answers"] for question in examples)
    assert {example.source for example in numeric_examples} == {"structured_answer_test_case"}
    assert {example.source for example in curated_examples} == {"structured_answer_test_case"}
    assert {example.rating for example in numeric_examples} >= {0.25, 0.85, 0.95}


# What is this even testing?
def test_curated_question_artifact_synthesizes_official_answer_examples(tmp_path: Path):
    curated = tmp_path / "developer_question_expansion.json"
    curated.write_text(
        """
        [
          {
            "certification": "AWS Certified Developer",
            "domain": "Application Integration",
            "difficulty": "Medium",
            "question": "Which configuration isolates failed SQS messages for a Lambda consumer?",
            "reference_answer": "Configure the Lambda event source mapping with an SQS dead-letter queue.",
            "key_concepts": ["Lambda event source mapping", "SQS dead-letter queue"],
            "acceptable_answers": ["AWS Lambda"],
            "original_multiple_choice": {
              "question": "Which configuration isolates failed SQS messages for a Lambda consumer?",
              "options": [
                {"option_id": "A", "text": "Configure an SQS dead-letter queue."},
                {"option_id": "B", "text": "Configure an SNS topic subscription."}
              ],
              "correct_option_ids": ["A"]
            }
          }
        ]
        """,
        encoding="utf-8",
    )

    examples = load_curated_question_regression_examples(curated)
    answers = {example.answer: example.rating for example in examples}

    assert answers["Configure an SQS dead-letter queue."] == 0.95
    assert answers["Configure the Lambda event source mapping with an SQS dead-letter queue."] == 0.95
    assert answers["Configure an SNS topic subscription."] == 0.25
    assert "AWS Lambda" not in answers


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
