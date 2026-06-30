import pytest

from scripts.generate_question_rewording_training_data import (
    DEFAULT_MAX_REWORDING_ROWS,
    HeuristicRewordingProvider,
    generate_rewording_rows,
)


def test_rewording_generator_creates_negative_curated_feedback_rows():
    question = {
        "certification": "Cloud Practitioner",
        "exam_code": "CLF-C02",
        "question": "Explain which AWS service should manage encryption keys.",
        "reference_answer": "Use AWS KMS.",
        "original_multiple_choice": {
            "question": "Which AWS service manages encryption keys?",
            "options": [{"option_id": "A", "text": "Use AWS KMS."}],
            "correct_option_ids": ["A"],
        },
    }

    rows = generate_rewording_rows([question], HeuristicRewordingProvider())

    assert rows == [
        {
            "schema_version": 3,
            "question": "Explain which AWS service should manage encryption keys.",
            "exam_code": "CLF-C02",
            "reference_answer": "Use AWS KMS.",
            "answer_given": (
                "This question is asking the learner to identify and explain "
                "which AWS service should manage encryption keys."
            ),
            "correct_rating": "D",
            "rating_given": "A",
            "feedback_text": (
                "Generated question-restatement negative example: this answer rewords the prompt "
                "without identifying the correct AWS service, feature, or reasoning."
            ),
            "original_multiple_choice": question["original_multiple_choice"],
        }
    ]


def test_rewording_generator_skips_duplicate_questions():
    question = {
        "exam_code": "CLF-C02",
        "question": "Explain which AWS service should manage encryption keys.",
        "reference_answer": "Use AWS KMS.",
    }
    duplicate = dict(question)
    duplicate["question"] = "  explain   which AWS service should manage encryption keys. "

    rows = generate_rewording_rows([question, duplicate], HeuristicRewordingProvider())

    assert len(rows) == 1
    assert rows[0]["question"] == question["question"]


def test_rewording_generator_caps_default_row_count():
    questions = [
        {
            "exam_code": "CLF-C02",
            "question": f"Explain which AWS service should handle task {index}.",
            "reference_answer": f"Use AWS service {index}.",
        }
        for index in range(DEFAULT_MAX_REWORDING_ROWS + 5)
    ]

    rows = generate_rewording_rows(questions, HeuristicRewordingProvider())

    assert len(rows) == DEFAULT_MAX_REWORDING_ROWS


def test_rewording_generator_rejects_empty_cap():
    with pytest.raises(ValueError, match="max_rows"):
        generate_rewording_rows([], HeuristicRewordingProvider(), max_rows=0)
