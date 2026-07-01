from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.questions.json_repository import question_from_json
from aws_certification_coach.ratings import score_to_letter
from scripts.generate_full_sentence_training_data import generate_full_sentence_rows


def test_full_sentence_generator_creates_a_grade_correction_rows():
    question = {
        "schema_version": 3,
        "certification": "Cloud Practitioner",
        "domain": "Security",
        "difficulty": "Easy",
        "question": "Explain which service manages encryption keys.",
        "reference_answer": "Use AWS KMS to create and manage encryption keys.",
        "key_concepts": ["AWS KMS", "encryption keys"],
        "acceptable_answers": ["AWS KMS"],
    }

    rows = generate_full_sentence_rows([question])

    assert rows == [
        {
            "schema_version": 3,
            "question": "Explain which service manages encryption keys.",
            "exam_code": "",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "answer_given": (
                "The best answer is to use AWS KMS to create and manage encryption keys. "
                "This addresses AWS KMS and encryption keys."
            ),
            "correct_rating": "A",
            "rating_given": "C",
            "feedback_text": (
                "Generated full-sentence positive example: this answer names the correct AWS service "
                "or feature and explains the relevant scenario concept."
            ),
        }
    ]


def test_generated_full_sentence_answers_score_as_a_grade():
    question = {
        "schema_version": 3,
        "certification": "Cloud Practitioner",
        "domain": "Billing",
        "difficulty": "Easy",
        "question_category": "cost_tradeoff",
        "question": "Explain which AWS service should track cost or usage thresholds and send alerts.",
        "reference_answer": "Use AWS Budgets to track cost or usage thresholds and send alerts.",
        "key_concepts": ["AWS Budgets", "cost thresholds", "usage thresholds", "alerts"],
        "acceptable_answers": ["AWS Budgets"],
    }
    row = generate_full_sentence_rows([question])[0]

    score = semantic_similarity_score(question_from_json(question), row["answer_given"])

    assert score_to_letter(score) == "A"
