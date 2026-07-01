import json

import app

from aws_certification_coach.domain import (
    EvaluationResult,
    MultipleChoiceOption,
    MultipleChoiceQuestion,
    Question,
    QuestionFilter,
)
from aws_certification_coach.evaluation.service import EvaluationService
from aws_certification_coach.evaluation.trained_classifier_provider import SemanticSimilarityEvaluatorProvider


class StaticProvider:
    def __init__(
        self,
        score: int,
        feedback: str = "",
        feedback_source: str = "",
        service_correct: bool = False,
        core_concept_correct: bool = False,
    ) -> None:
        self.score = score
        self.feedback = feedback
        self.feedback_source = feedback_source
        self.service_correct = service_correct
        self.core_concept_correct = core_concept_correct

    def evaluate(self, prompt: str, question: Question, user_answer: str) -> str:
        del prompt, question, user_answer
        return json.dumps(
            {
                "score": self.score,
                "missing_concepts": [],
                "suggested_improvements": [],
                "service_correct": self.service_correct,
                "core_concept_correct": self.core_concept_correct,
                "feedback": self.feedback,
                "feedback_source": self.feedback_source,
                "detailed_answer": "Use AWS KMS to manage encryption keys.",
            }
        )


QUESTION = Question(
    schema_version=1,
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


def test_structured_feedback_fields_are_preserved_from_provider_response():
    result = EvaluationService(
        StaticProvider(
            82,
            service_correct=True,
            core_concept_correct=False,
        )
    ).evaluate(QUESTION, "AWS KMS")

    assert result.service_correct is True
    assert result.core_concept_correct is False


def test_valid_wrong_service_name_is_not_reported_as_misspelled():
    question = Question(
        schema_version=1,
        certification="Developer Associate",
        domain="Development with AWS Services",
        difficulty="Easy",
        question="Which service queues messages for asynchronous processing?",
        reference_answer="Use Amazon SQS.",
        key_concepts=["Amazon SQS", "message queue"],
        acceptable_answers=["Amazon SQS"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which service queues messages for asynchronous processing?",
            options=[
                MultipleChoiceOption("A", "Use Amazon SQS."),
                MultipleChoiceOption("B", "Use Amazon SNS."),
            ],
            correct_option_ids=["A"],
        ),
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(question, "Use Amazon SNS.")

    assert result.score <= 49
    assert result.feedback == "This exact service answer is not in the question's correct answer list."


def test_common_misconception_answer_gets_specific_feedback():
    question = Question(
        certification="Cloud Practitioner",
        domain="Billing",
        difficulty="Easy",
        question="Explain which service tracks cost thresholds and sends alerts.",
        reference_answer="Use AWS Budgets to track thresholds and send alerts.",
        key_concepts=["AWS Budgets", "cost thresholds", "alerts"],
        common_misconceptions=["AWS CloudTrail is the best fit for this requirement."],
        acceptable_answers=["AWS Budgets"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(question, "Use AWS CloudTrail.")

    assert result.score <= 65
    assert result.feedback == (
        "This answer appears to rely on a common misconception: "
        "AWS CloudTrail is the best fit for this requirement."
    )


def test_must_not_claim_answer_gets_stronger_feedback():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Explain which service should manage encryption keys.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
        must_not_claim=["Amazon S3 satisfies the scenario better than AWS KMS."],
        do_not_claim_explanation=["AWS KMS is a better option because it is designed to manage encryption keys."],
        acceptable_answers=["AWS KMS"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(question, "Use Amazon S3.")

    assert result.score <= 49
    assert result.feedback == "AWS KMS is a better option because it is designed to manage encryption keys."


def test_must_not_claim_matches_short_service_answer_without_aws_prefix():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Management and Governance",
        difficulty="Easy",
        question="Explain which service tracks resource configuration history and evaluates compliance.",
        reference_answer="Use AWS Config.",
        key_concepts=["AWS Config", "configuration history", "compliance rules"],
        must_not_claim=["AWS CloudTrail satisfies the scenario better than AWS Config."],
        do_not_claim_explanation=[
            (
                "AWS Config is a better option because it tracks resource configuration history.\n\n"
                "AWS CloudTrail records API activity, so it does not satisfy this scenario requirement."
            )
        ],
        acceptable_answers=["AWS Config"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(question, "CloudTrail")

    assert result.score <= 49
    assert result.feedback == question.do_not_claim_explanation[0]
    assert "\n\nAWS CloudTrail" in result.feedback


def test_negated_misconception_does_not_trigger_feedback():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Billing",
        difficulty="Easy",
        question="Explain which service tracks cost thresholds and sends alerts.",
        reference_answer="Use AWS Budgets to track thresholds and send alerts.",
        key_concepts=["AWS Budgets", "cost thresholds", "alerts"],
        common_misconceptions=["AWS CloudTrail is the best fit for this requirement."],
        acceptable_answers=["AWS Budgets"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        "Do not use AWS CloudTrail; use AWS Budgets for alerts.",
    )

    assert "common misconception" not in result.feedback


def test_framed_question_restatement_receives_restatement_feedback():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Explain which AWS service should manage encryption keys.",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS", "encryption keys"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        "This question is asking the learner to identify which AWS service should manage encryption keys.",
    )

    assert result.score <= 25
    assert result.feedback == "This answer restates the question without identifying and explaining the solution."


def test_correct_paraphrase_is_not_downgraded_as_question_rewording():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Billing",
        difficulty="Easy",
        question="Explain which AWS service should track cost or usage thresholds and send alerts.",
        reference_answer="Use AWS Budgets to track cost or usage thresholds and send alerts.",
        key_concepts=["AWS Budgets", "cost thresholds", "usage thresholds", "alerts"],
        acceptable_answers=["AWS Budgets"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        "AWS Budgets alerts teams when actual or forecasted spending crosses cost or usage thresholds.",
    )

    assert result.score >= 90
    assert result.feedback == ""


def test_correct_service_with_wrong_reasoning_receives_b_band_feedback():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Billing",
        difficulty="Easy",
        question="Explain which AWS service should track cost or usage thresholds and send alerts.",
        reference_answer="Use AWS Budgets to track cost or usage thresholds and send alerts.",
        key_concepts=["AWS Budgets", "cost thresholds", "usage thresholds", "alerts"],
        acceptable_answers=["AWS Budgets"],
        common_misconceptions=["AWS CloudTrail is the best fit for this requirement."],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        "Use AWS Budgets because it records API activity and audits account events.",
    )

    assert 80 <= result.score <= 89
    assert result.service_correct is True
    assert result.core_concept_correct is False
    assert result.feedback == "The answer names the correct service but includes reasoning for a different AWS concept."


def test_service_description_without_required_service_name_does_not_receive_b_level_score():
    question = Question(
        schema_version=1,
        certification="Solutions Architect Associate",
        domain="Database",
        difficulty="Medium",
        question=(
            "Explain which AWS service or feature should replicate tables across Regions "
            "for low-latency multi-Region access and resilience."
        ),
        reference_answer=(
            "Use DynamoDB global tables to replicate tables across Regions for low-latency "
            "multi-Region access and resilience."
        ),
        key_concepts=["DynamoDB global tables", "multi-Region", "replication", "low latency"],
        acceptable_answers=["DynamoDB global tables"],
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        "Use a global table replication feature across Regions for low latency.",
    )

    assert result.score <= 79
    assert result.feedback == "Name the specific AWS service or feature required by the question."


def test_artifact_review_accepts_exact_corrected_config_as_correct_answer():
    question = Question(
        schema_version=1,
        certification="AWS Certified Developer",
        domain="Development with AWS Services",
        difficulty="Medium",
        question_type="artifact_review",
        question="Review the SDK code.",
        reference_answer="Use a paginator so the function reads every page of ListObjectsV2 results.",
        key_concepts=["SDK pagination", "S3 ListObjectsV2", "paginator"],
        required_concepts=["SDK pagination", "S3 ListObjectsV2", "paginator"],
        artifact_type="sdk_usage",
        artifact_language="python",
        artifact_body=(
            "import boto3\n\n"
            "s3 = boto3.client(\"s3\")\n\n"
            "def all_keys(bucket):\n"
            "    response = s3.list_objects_v2(Bucket=bucket)\n"
            "    return [item[\"Key\"] for item in response.get(\"Contents\", [])]"
        ),
        artifact_corrected=(
            "import boto3\n\n"
            "s3 = boto3.client(\"s3\")\n\n"
            "def all_keys(bucket):\n"
            "    paginator = s3.get_paginator(\"list_objects_v2\")\n"
            "    keys = []\n"
            "    for page in paginator.paginate(Bucket=bucket):\n"
            "        keys.extend(item[\"Key\"] for item in page.get(\"Contents\", []))\n"
            "    return keys"
        ),
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(question, question.artifact_corrected)

    assert result.score >= 90
    assert result.feedback == ""


def test_artifact_review_accepts_exact_changed_corrected_lines_as_correct_answer():
    question = Question(
        schema_version=1,
        certification="AWS Certified Developer",
        domain="Security",
        difficulty="Medium",
        question_type="artifact_review",
        question="Review this policy.",
        reference_answer="Scope the policy resource to the required S3 object ARN.",
        key_concepts=["IAM policy", "least privilege", "S3 object ARN"],
        required_concepts=["IAM policy", "least privilege", "S3 object ARN"],
        artifact_type="iam_policy",
        artifact_language="json",
        artifact_body='{\n  "Resource": "*"\n}',
        artifact_corrected='{\n  "Resource": "arn:aws:s3:::example-bucket/reports/*"\n}',
    )

    result = EvaluationService(SemanticSimilarityEvaluatorProvider()).evaluate(
        question,
        '+  "Resource": "arn:aws:s3:::example-bucket/reports/*"',
    )

    assert result.score >= 90
    assert result.feedback == ""


def test_app_hides_artifact_review_questions_unless_enabled(monkeypatch):
    regular_question = Question(
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Which service manages encryption keys?",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
    )
    artifact_question = Question(
        certification="AWS Certified Developer",
        domain="Security",
        difficulty="Medium",
        question_type="artifact_review",
        question="Review this policy.",
        reference_answer="Scope the policy.",
        key_concepts=["IAM policy"],
        artifact_body='{"Resource": "*"}',
    )

    monkeypatch.delenv("SHOW_ARTIFACT_REVIEW", raising=False)
    assert app._visible_questions([regular_question, artifact_question]) == [regular_question]

    monkeypatch.setenv("SHOW_ARTIFACT_REVIEW", "1")
    assert app._visible_questions([regular_question, artifact_question]) == [regular_question, artifact_question]


def test_app_filters_questions_by_question_category():
    security_question = Question(
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Which service manages encryption keys?",
        reference_answer="Use AWS KMS.",
        key_concepts=["AWS KMS"],
        question_category="security_identity",
    )
    cost_question = Question(
        certification="Cloud Practitioner",
        domain="Billing",
        difficulty="Easy",
        question="Which service tracks thresholds?",
        reference_answer="Use AWS Budgets.",
        key_concepts=["AWS Budgets"],
        question_category="cost_tradeoff",
    )

    filtered = app._filter_questions(
        [security_question, cost_question],
        QuestionFilter(question_category="cost_tradeoff"),
    )

    assert filtered == [cost_question]


def test_app_renders_original_and_corrected_config_after_answer(monkeypatch):
    calls = []
    question = Question(
        certification="AWS Certified Developer",
        domain="Security",
        difficulty="Medium",
        question_type="artifact_review",
        question="Review this policy.",
        reference_answer="Scope the policy.",
        key_concepts=["IAM policy"],
        artifact_type="iam_policy",
        artifact_language="json",
        artifact_body='{\n  "Resource": "*"\n}',
        artifact_context="A Lambda role needs narrow S3 read access.",
        artifact_corrected='{\n  "Resource": "arn:aws:s3:::example-bucket/reports/*"\n}',
    )

    monkeypatch.setattr(app.st, "caption", lambda value: calls.append(("caption", value)))
    monkeypatch.setattr(
        app,
        "_render_artifact_block",
        lambda *args, **kwargs: calls.append(("block", args, kwargs)),
    )

    app._render_artifact(question, show_corrected=True)

    assert ("caption", "iam_policy | json") in calls
    assert calls[1] == (
        "block",
        ("Original Config", question.artifact_body, question.artifact_language),
        {"context": question.artifact_context, "expanded": False},
    )
    assert calls[2] == (
        "block",
        ("Corrected Config", question.artifact_corrected, question.artifact_language),
        {"expanded": True, "original_body": question.artifact_body},
    )


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


def test_app_can_render_multiple_choice_answers_without_highlighting_correct_option(monkeypatch):
    rendered = []
    monkeypatch.setattr(app.st, "write", lambda value: rendered.append(("write", value)))
    monkeypatch.setattr(app.st, "success", lambda value: rendered.append(("success", value)))
    monkeypatch.setattr(app.st, "markdown", lambda value: rendered.append(("markdown", value)))
    original = MultipleChoiceQuestion(
        question="Which service manages encryption keys?",
        options=[
            MultipleChoiceOption("A", "Use AWS KMS."),
            MultipleChoiceOption("B", "Use Amazon S3."),
        ],
        correct_option_ids=["A"],
    )

    app._render_original_multiple_choice(original, highlight_correct=False)

    assert ("write", "A. Use AWS KMS.") in rendered
    assert ("write", "B. Use Amazon S3.") in rendered
    assert not any(kind == "success" for kind, _value in rendered)


def test_app_show_answers_path_omits_documentation_links(monkeypatch):
    rendered = []
    monkeypatch.setattr(app.st, "write", lambda value: rendered.append(("write", value)))
    monkeypatch.setattr(app.st, "success", lambda value: rendered.append(("success", value)))
    monkeypatch.setattr(app.st, "markdown", lambda value: rendered.append(("markdown", value)))
    original = MultipleChoiceQuestion(
        question="Which service manages encryption keys?",
        options=[
            MultipleChoiceOption("A", "Use AWS KMS.", "https://docs.aws.amazon.com/kms/"),
            MultipleChoiceOption("B", "Use Amazon S3.", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/"),
        ],
        correct_option_ids=["A"],
        source_name="AWS Documentation: AWS KMS",
        source_url="https://docs.aws.amazon.com/kms/",
    )

    app._render_original_multiple_choice(original, highlight_correct=False)

    assert ("write", "A. Use AWS KMS.") in rendered
    assert not any(value == "### Documentation" for _kind, value in rendered)
    assert not any("https://docs.aws.amazon.com" in str(value) for _kind, value in rendered)


def test_app_disambiguates_repeated_service_documentation_labels(monkeypatch):
    rendered = []
    monkeypatch.setattr(app.st, "write", lambda value: rendered.append(("write", value)))
    monkeypatch.setattr(app.st, "success", lambda value: rendered.append(("success", value)))
    monkeypatch.setattr(app.st, "markdown", lambda value: rendered.append(("markdown", value)))
    original = MultipleChoiceQuestion(
        question="Which DynamoDB API pattern should the developer use?",
        options=[
            MultipleChoiceOption(
                "A",
                "Use DynamoDB TransactWriteItems.",
                "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html",
                {"service_name": "Amazon DynamoDB"},
            ),
            MultipleChoiceOption(
                "B",
                "Enable DynamoDB Streams only.",
                "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html",
                {"service_name": "Amazon DynamoDB"},
            ),
        ],
        correct_option_ids=["A"],
    )

    app._render_multiple_choice_source_documentation(original)

    assert (
        "markdown",
        "- [DynamoDB TransactWriteItems](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transactions.html)\n"
        "- [Enable DynamoDB Streams only](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)\n",
    ) in rendered
