from scripts.generate_question_rewording_training_data import (
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
