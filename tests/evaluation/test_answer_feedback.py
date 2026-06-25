import json

import app

from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.evaluation.service import EvaluationService


class StaticProvider:
    def __init__(self, score: int, feedback: str = "") -> None:
        self.score = score
        self.feedback = feedback

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt, question, user_answer
        return json.dumps(
            {
                "score": self.score,
                "missing_concepts": [],
                "suggested_improvements": [],
                "feedback": self.feedback,
                "detailed_answer": "Use AWS KMS to manage encryption keys.",
            }
        )


QUESTION = Question(
    certification="Cloud Practitioner",
    domain="Security",
    difficulty="Easy",
    question="Which service manages encryption keys?",
    reference_answer="Use AWS KMS to manage encryption keys.",
    key_concepts=["AWS KMS", "encryption keys"],
)


def test_terse_b_answer_receives_complete_sentence_guidance():
    result = EvaluationService(StaticProvider(80)).evaluate(QUESTION, "AWS KMS")

    assert result.feedback == (
        "For full credit, state your answer in a complete sentence and explain why the service fits the requirement."
    )


def test_non_a_answer_preserves_specific_provider_feedback():
    result = EvaluationService(StaticProvider(65, "The service name is misspelled.")).evaluate(
        QUESTION,
        "AWS Key Store",
    )

    assert result.feedback == "The service name is misspelled."


def test_app_renders_feedback_only_for_non_a_answers(monkeypatch):
    rendered = []
    monkeypatch.setattr(app.st, "write", lambda value: rendered.append(("write", value)))
    monkeypatch.setattr(app.st, "info", lambda value: rendered.append(("info", value)))

    app._render_answer_feedback(80, "Explain why the service fits.")
    app._render_answer_feedback(95, "This should not display.")

    assert rendered == [
        ("write", "Feedback"),
        ("info", "Explain why the service fits."),
    ]


def test_app_lists_all_multiple_choice_source_links_under_answers(monkeypatch):
    rendered = []
    monkeypatch.setattr(app.st, "write", lambda value: rendered.append(("write", value)))
    monkeypatch.setattr(app.st, "success", lambda value: rendered.append(("success", value)))
    monkeypatch.setattr(app.st, "markdown", lambda value: rendered.append(("markdown", value)))
    monkeypatch.setattr(app.st, "caption", lambda value: rendered.append(("caption", value)))
    original = MultipleChoiceQuestion(
        question="Which service manages encryption keys?",
        options=[
            MultipleChoiceOption("A", "Use AWS KMS.", "https://docs.aws.amazon.com/kms/"),
            MultipleChoiceOption("B", "Use Amazon S3.", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/"),
            MultipleChoiceOption("C", "Use AWS Lambda."),
        ],
        correct_option_ids=["A"],
        source_name="AWS Documentation: AWS KMS",
    )

    app._render_original_multiple_choice(original)
    app._render_multiple_choice_source_documentation(original)

    assert ("markdown", "### Multiple-choice Answers") in rendered
    assert ("markdown", "### Additional Documentation") in rendered
    assert ("markdown", "- [AWS KMS](https://docs.aws.amazon.com/kms/)\n- [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)\n") in rendered
    assert ("write", "C. Use AWS Lambda.") in rendered
