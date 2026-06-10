from pathlib import Path

import json

from aws_certification_coach.domain import Question
from aws_certification_coach.feedback import UserFeedbackRepository
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import letter_to_binary_label, letter_to_numeric, score_to_letter
from aws_certification_coach.training.dataset import (
    load_feedback_classification_examples,
    load_feedback_regression_examples,
)


def test_feedback_repository_saves_letter_grades_without_numeric_values(tmp_path: Path):
    path = tmp_path / "generated" / "user_feedback.json"
    question = _question()

    UserFeedbackRepository(path).submit(question, "AWS", rating_given="A", correct_rating="F")

    rows = json.loads(path.read_text(encoding="utf-8"))
    assert rows == [
        {
            "question_id": "AWS-APP-020",
            "question": question.question,
            "reference_answer": question.reference_answer,
            "answer_given": "AWS",
            "correct_rating": "F",
            "rating_given": "A",
        }
    ]


def test_feedback_loaders_convert_correct_letter_grade_in_background(tmp_path: Path):
    path = tmp_path / "feedback.json"
    path.write_text(
        json.dumps(
            [
                {
                    "question_id": "AWS-APP-020",
                    "question": "ignored when question_id is present",
                    "reference_answer": "Use AWS KMS",
                    "answer_given": "AWS",
                    "correct_rating": "F",
                    "rating_given": "A",
                }
            ]
        ),
        encoding="utf-8",
    )
    questions = {"AWS-APP-020": _question()}

    regression = load_feedback_regression_examples(path, questions)
    classification = load_feedback_classification_examples(path, questions)

    assert regression[0].rating == 0.25
    assert classification[0].label == 0


def test_rating_conversions_follow_display_grade_boundaries():
    assert score_to_letter(70) == "C"
    assert letter_to_numeric("C") == 0.75
    assert letter_to_binary_label("C") == 1
    assert letter_to_binary_label("D") == 0


def test_curated_feedback_matches_generated_questions_and_converts_to_numbers():
    project_root = Path(__file__).resolve().parents[1]
    question_path = project_root / "data" / "generated" / "questions_with_answers_generated.json"
    feedback_path = project_root / "data" / "curated" / "curated_training_data.json"
    questions = JsonQuestionRepository(question_path).all()
    questions_by_id = {question.question_id: question for question in questions}

    regression = load_feedback_regression_examples(feedback_path, questions_by_id)
    classification = load_feedback_classification_examples(feedback_path, questions_by_id)

    assert len(regression) == 5
    assert len(classification) == 5
    assert {example.rating for example in regression} == {0.65, 0.25}
    assert {example.label for example in classification} == {0}


def _question() -> Question:
    return Question(
        question_id="AWS-APP-020",
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Explain which AWS service should manage encryption keys.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
    )
