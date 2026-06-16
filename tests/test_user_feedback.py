from pathlib import Path

import json

import pytest

from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.feedback import UserFeedbackRepository
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import (
    letter_to_binary_label,
    letter_to_grade_band,
    letter_to_numeric,
    score_to_letter,
)
from aws_certification_coach.training.dataset import (
    load_feedback_classification_examples,
    load_feedback_regression_examples,
)
from scripts.curated_failure_report import _conflicting_labels


def test_feedback_repository_saves_letter_grades_without_numeric_values(tmp_path: Path):
    path = tmp_path / "generated" / "user_feedback.json"
    question = _question()

    UserFeedbackRepository(path).submit(question, "AWS", rating_given="A", correct_rating="F")

    rows = json.loads(path.read_text(encoding="utf-8"))
    assert rows == [
        {
            "schema_version": 2,
            "question": question.question,
            "reference_answer": question.reference_answer,
            "original_multiple_choice": {
                "question": "Which AWS service manages encryption keys?",
                "options": [
                    {"option_id": "A", "text": "Use AWS KMS."},
                    {"option_id": "B", "text": "Use Amazon S3."},
                ],
                "correct_option_ids": ["A"],
                "explanation": "AWS KMS manages encryption keys.",
                "source_name": "AWS KMS documentation",
                "source_url": "https://docs.aws.amazon.com/kms/",
                "source_license_notes": "AWS documentation used for topic grounding.",
            },
            "answer_given": "AWS",
            "correct_rating": "F",
            "rating_given": "A",
        }
    ]


def test_feedback_repository_appends_to_existing_v1_records(tmp_path: Path):
    path = tmp_path / "generated" / "user_feedback.v1.json"
    path.parent.mkdir(parents=True)
    path.write_text("[]\n", encoding="utf-8")

    UserFeedbackRepository(path).submit(_question(), "AWS KMS", rating_given="A", correct_rating="A")

    rows = json.loads(path.read_text(encoding="utf-8"))
    assert rows[0]["schema_version"] == 2
    assert set(rows[0]) == {
        "schema_version",
        "question",
        "reference_answer",
        "original_multiple_choice",
        "answer_given",
        "correct_rating",
        "rating_given",
    }
    assert rows[0]["original_multiple_choice"]["correct_option_ids"] == ["A"]


def test_feedback_repository_exports_empty_json_when_artifact_is_missing(tmp_path: Path):
    path = tmp_path / "generated" / "user_feedback.v1.json"

    exported = UserFeedbackRepository(path).export_json()

    assert exported == "[]\n"


def test_feedback_loaders_match_full_question_text_and_convert_grade(tmp_path: Path):
    path = tmp_path / "feedback.json"
    path.write_text(
        json.dumps(
            [
                {
                    "legacy_marker": "ignored",
                    "question": _question().question,
                    "reference_answer": "Use AWS KMS",
                    "answer_given": "AWS",
                    "correct_rating": "F",
                    "rating_given": "A",
                }
            ]
        ),
        encoding="utf-8",
    )
    questions = [_question()]

    regression = load_feedback_regression_examples(path, questions)
    classification = load_feedback_classification_examples(path, questions)

    assert regression[0].rating == 0.25
    assert classification[0].label == 0
    assert regression[0].question == _question()


def test_feedback_loader_can_match_using_original_multiple_choice_question(tmp_path: Path):
    path = tmp_path / "feedback.json"
    path.write_text(
        json.dumps(
            [
                {
                    "question": "",
                    "reference_answer": "",
                    "original_multiple_choice": {
                        "question": "Which AWS service manages encryption keys?",
                        "options": [],
                        "correct_option_ids": [],
                    },
                    "answer_given": "AWS",
                    "correct_rating": "F",
                    "rating_given": "A",
                }
            ]
        ),
        encoding="utf-8",
    )

    examples = load_feedback_classification_examples(path, [_question()])

    assert examples[0].question == _question()


def test_rating_conversions_follow_display_grade_boundaries():
    assert score_to_letter(70) == "C"
    assert letter_to_numeric("C") == 0.75
    assert letter_to_binary_label("C") == 1
    assert letter_to_binary_label("D") == 0


def test_letter_grades_map_to_three_evaluation_bands():
    assert letter_to_grade_band("A") == "A/B"
    assert letter_to_grade_band("B") == "A/B"
    assert letter_to_grade_band("C") == "C/D"
    assert letter_to_grade_band("D") == "C/D"
    assert letter_to_grade_band("F") == "F"


def test_curated_label_conflicts_only_count_cross_band_disagreements():
    rows = [
        {"question": "Question one", "answer_given": "Answer", "correct_rating": "A"},
        {"question": "Question one", "answer_given": "Answer", "correct_rating": "B"},
        {"question": "Question two", "answer_given": "Answer", "correct_rating": "B"},
        {"question": "Question two", "answer_given": "Answer", "correct_rating": "D"},
    ]

    conflicts = _conflicting_labels(rows)

    assert ("question one", "answer") not in conflicts
    assert conflicts[("question two", "answer")] == {"B", "D"}

def _question() -> Question:
    return Question(
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Explain which AWS service should manage encryption keys.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which AWS service manages encryption keys?",
            options=[
                MultipleChoiceOption(option_id="A", text="Use AWS KMS."),
                MultipleChoiceOption(option_id="B", text="Use Amazon S3."),
            ],
            correct_option_ids=["A"],
            explanation="AWS KMS manages encryption keys.",
            source_name="AWS KMS documentation",
            source_url="https://docs.aws.amazon.com/kms/",
            source_license_notes="AWS documentation used for topic grounding.",
        ),
    )
