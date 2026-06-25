import json

import app

from aws_certification_coach.domain import EvaluationResult, MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import SemanticSimilarityEvaluatorProvider


class StaticProvider:
    def __init__(self, score: int, feedback: str = "", feedback_source: str = "") -> None:
        self.score = score
        self.feedback = feedback
        self.feedback_source = feedback_source

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt, question, user_answer
        return json.dumps(
            {
                "score": self.score,
                "missing_concepts": [],
                "suggested_improvements": [],
                "feedback": self.feedback,
                "feedback_source": self.feedback_source,
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

    assert result.feedback == "Please write full sentence answers for full credit."


def test_non_a_answer_preserves_specific_provider_feedback():
    result = EvaluationService(StaticProvider(65, "The service name is misspelled.")).evaluate(
        QUESTION,
        "AWS Key Store",
    )

    assert result.feedback == "The service name is misspelled."


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
            MultipleChoiceOption(
                "C",
                "Configure an Amazon Cognito user pool.",
                "https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html",
                {"service_name": "Amazon Cognito"},
            ),
        ],
        correct_option_ids=["A"],
        source_name="AWS Documentation: AWS KMS",
    )

    app._render_original_multiple_choice(original)
    app._render_multiple_choice_source_documentation(original)

    assert ("markdown", "### Multiple-choice Answers") in rendered
    assert ("markdown", "### Documentation") in rendered
    assert (
        "markdown",
        "- [AWS KMS](https://docs.aws.amazon.com/kms/)\n"
        "- [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)\n"
        "- [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html)\n",
    ) in rendered
    assert ("write", "C. Configure an Amazon Cognito user pool.") in rendered
