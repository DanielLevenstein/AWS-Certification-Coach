#!/usr/bin/env python3
"""Generate self-authored Developer Associate freeform questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.config import current_schema_version
from aws_certification_coach.question_fidelity.model import QuestionFidelityModel
try:
    from generate_app_question_artifacts import documentation_url_for_option, distractor_feedback, service_metadata_for_option
except ModuleNotFoundError:  # Imported as scripts.generate_developer_question_artifacts in tests.
    from scripts.generate_app_question_artifacts import (
        distractor_feedback,
        documentation_url_for_option,
        service_metadata_for_option,
    )


QUESTION_TEMPLATES = {
    "dva-lambda-sqs-dlq": "A Lambda function processes messages from an SQS queue. A few messages repeatedly fail and delay later processing. Which configuration should the developer use to isolate failed messages while allowing successful messages to continue?",
    "dva-api-gateway-lambda-auth": "A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?",
    "dva-dynamodb-conditional-write": "Two application instances may try to create the same DynamoDB item at the same time. Which DynamoDB write approach should the developer use to prevent replacing an existing item?",
    "dva-codepipeline-codebuild": "A development team wants its release pipeline to compile code and run unit tests automatically before deployment. Which AWS service should be added as the build action?",
    "dva-xray-tracing": "A serverless application has intermittent latency across several downstream calls. Which AWS service should the developer use to trace each request through the distributed workflow?",
    "dva-lambda-env-vars": "A Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime?",
    "dva-secrets-manager-rotation": "A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?",
    "dva-sqs-visibility-timeout": "An SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message?",
    "dva-dynamodb-streams-lambda": "An application must run code whenever items in a DynamoDB table are inserted, updated, or deleted. Which event-driven pattern should the developer configure?",
    "dva-api-gateway-throttling": "A public API must protect its backend from sudden request spikes by limiting client request rates. Which API Gateway feature should the developer configure?",
    "dva-codebuild-buildspec": "A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?",
    "dva-eventbridge-schedule-lambda": "A serverless maintenance task needs to invoke a Lambda function every hour. Which AWS service feature should the developer configure?",
}

DISTRACTORS = {
    "dva-lambda-sqs-dlq": ["Configure an SNS topic subscription.", "Add a CloudWatch alarm only.", "Use Lambda provisioned concurrency."],
    "dva-api-gateway-lambda-auth": ["Attach an EC2 security group.", "Create an AWS WAF rate-based rule only.", "Store the token in AWS Secrets Manager."],
    "dva-dynamodb-conditional-write": ["Run a table scan before each write.", "Increase write capacity units.", "Replicate the table with global tables."],
    "dva-codepipeline-codebuild": ["Use CodeDeploy lifecycle hooks only.", "Run commands manually on an EC2 instance.", "Create a CloudWatch dashboard."],
    "dva-xray-tracing": ["Use CloudTrail event history.", "Use AWS Config resource history.", "Increase Lambda memory without tracing."],
    "dva-lambda-env-vars": ["Store the values in CloudWatch Logs.", "Create an IAM role for each value.", "Use Lambda provisioned concurrency."],
    "dva-secrets-manager-rotation": ["Store the password in a Lambda environment variable.", "Use AWS KMS keys alone.", "Place the value in a CloudFormation output."],
    "dva-sqs-visibility-timeout": ["Increase the message retention period.", "Configure a delay queue only.", "Add an SNS topic subscription."],
    "dva-dynamodb-streams-lambda": ["Schedule a table scan from EventBridge.", "Read CloudTrail management events.", "Increase DynamoDB write capacity."],
    "dva-api-gateway-throttling": ["Set Lambda environment variables.", "Create a CloudWatch alarm only.", "Use an SQS visibility timeout."],
    "dva-codebuild-buildspec": ["Define the phases in a CodeDeploy AppSpec file.", "Put commands in an IAM policy.", "Create an API Gateway stage variable."],
    "dva-eventbridge-schedule-lambda": ["Configure an SQS dead-letter queue only.", "Use CloudTrail event history.", "Run the function from a local cron job."],
}

CORRECT_OPTIONS = {
    "dva-lambda-sqs-dlq": "Configure an SQS dead-letter queue.",
    "dva-api-gateway-lambda-auth": "Use an API Gateway Lambda authorizer.",
    "dva-dynamodb-conditional-write": "Use a DynamoDB conditional write.",
    "dva-codepipeline-codebuild": "Use AWS CodeBuild.",
    "dva-xray-tracing": "Use AWS X-Ray.",
    "dva-lambda-env-vars": "Use Lambda environment variables.",
    "dva-secrets-manager-rotation": "Use AWS Secrets Manager.",
    "dva-sqs-visibility-timeout": "Adjust the SQS visibility timeout.",
    "dva-dynamodb-streams-lambda": "Use DynamoDB Streams with Lambda.",
    "dva-api-gateway-throttling": "Configure API Gateway throttling.",
    "dva-codebuild-buildspec": "Use a CodeBuild buildspec file.",
    "dva-eventbridge-schedule-lambda": "Use an EventBridge scheduled rule.",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("data/original_questions/developer_associate_sources.json"))
    parser.add_argument("--output", type=Path, default=Path("data/generated/developer_question_expansion.json"))
    parser.add_argument("--app-output", type=Path, default=None)
    args = parser.parse_args()

    sources = json.loads(args.sources.read_text(encoding="utf-8"))
    questions = build_questions(sources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(questions, indent=2) + "\n", encoding="utf-8")
    if args.app_output is not None:
        existing = json.loads(args.app_output.read_text(encoding="utf-8")) if args.app_output.exists() else []
        args.app_output.parent.mkdir(parents=True, exist_ok=True)
        args.app_output.write_text(json.dumps([*existing, *questions], indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(questions)} Developer Associate questions into {args.output}.")


def build_questions(sources: list[dict[str, object]]) -> list[dict[str, object]]:
    model = QuestionFidelityModel()
    schema_version = current_schema_version("QUESTION_SCHEMA_VERSION")
    questions: list[dict[str, object]] = []
    for source in sources:
        source_id = str(source["source_id"])
        service = str(source["services"][0])
        concepts = [str(concept) for concept in source["concepts"]]
        question_text = _generated_question(source, source_id)
        reference_answer = _reference_answer(source, source_id, service)
        options = [_option("A", _correct_option(source, source_id), str(source["source_url"]))]
        options.extend(
            _option(option_id, text, documentation_url_for_option(text))
            for option_id, text in zip(["B", "C", "D"], _distractors(source, source_id), strict=True)
        )
        row = {
            "schema_version": schema_version,
            "certification": source["certification"],
            "exam_code": source.get("exam_code", ""),
            "domain": source["domain"],
            "difficulty": source["difficulty"],
            "question_type": str(source.get("question_type", "scenario_multiple_choice")),
            "question": question_text,
            "reference_answer": reference_answer,
            "key_concepts": concepts,
            **_rubric_metadata(source, source_id, service, concepts, reference_answer),
            "original_multiple_choice": {
                "question": question_text,
                "options": options,
                "correct_option_ids": ["A"],
                "explanation": reference_answer,
                "source_name": source["source_name"],
                "source_url": source["source_url"],
                "source_license_notes": source["source_license_notes"],
            },
            "source_examples": [source_id],
            "exam_calibration": {
                "source_type": source["source_type"],
                "exam_style_notes": source["exam_style_notes"],
                "reasoning_pattern": source["reasoning_pattern"],
            },
        }
        row.update(_artifact_metadata(source))
        row["question_fidelity"] = model.score(source, row).__dict__
        questions.append(row)
    return questions


def _option(option_id: str, text: str, source_url: str = "") -> dict[str, str]:
    payload = {"option_id": option_id, "text": text}
    if source_url:
        payload["source_url"] = source_url
        metadata = service_metadata_for_option(text, source_url)
        if metadata:
            payload["metadata"] = metadata
    return payload


def _rubric_metadata(
    source: dict[str, object],
    source_id: str,
    service: str,
    concepts: list[str],
    reference_answer: str,
) -> dict[str, list[str]]:
    distractors = _distractors(source, source_id)
    correct_option = _correct_option(source, source_id)
    return {
        "required_concepts": concepts,
        "bonus_concepts": [],
        "common_misconceptions": [f"{distractor} is the best fit for this scenario." for distractor in distractors],
        "acceptable_answers": [correct_option, reference_answer, service],
        "must_not_claim": [f"{distractor} satisfies the scenario better than {service}." for distractor in distractors],
        "do_not_claim_explanation": [
            distractor_feedback(service, distractor, _scenario_purpose(source, reference_answer))
            for distractor in distractors
        ],
    }


def _generated_question(source: dict[str, object], source_id: str) -> str:
    if source.get("generated_question"):
        return str(source["generated_question"])
    return QUESTION_TEMPLATES[source_id]


def _correct_option(source: dict[str, object], source_id: str) -> str:
    if source.get("correct_option"):
        return str(source["correct_option"])
    return CORRECT_OPTIONS[source_id]


def _distractors(source: dict[str, object], source_id: str) -> list[str]:
    if source.get("distractors"):
        return [str(distractor) for distractor in source["distractors"]]
    return DISTRACTORS[source_id]


def _reference_answer(source: dict[str, object], source_id: str, service: str) -> str:
    if source.get("reference_answer"):
        return str(source["reference_answer"])
    answers = {
        "dva-lambda-sqs-dlq": "Configure the Lambda event source mapping with an SQS dead-letter queue so failed messages can be isolated after retries.",
        "dva-api-gateway-lambda-auth": "Use an API Gateway Lambda authorizer to run custom authorization logic before invoking the backend Lambda integration.",
        "dva-dynamodb-conditional-write": "Use a DynamoDB conditional write with a condition expression such as attribute_not_exists to avoid overwriting an existing item.",
        "dva-codepipeline-codebuild": "Add AWS CodeBuild as a CodePipeline build stage to compile the application and run tests automatically.",
        "dva-xray-tracing": "Use AWS X-Ray distributed tracing and service maps to follow requests and identify latency across downstream calls.",
        "dva-lambda-env-vars": "Use Lambda environment variables to provide non-secret function configuration values that can differ by deployment environment.",
        "dva-secrets-manager-rotation": "Use AWS Secrets Manager to store database credentials and configure scheduled rotation for the secret.",
        "dva-sqs-visibility-timeout": "Adjust the SQS visibility timeout so a message remains hidden from other consumers while the current worker processes it.",
        "dva-dynamodb-streams-lambda": "Enable DynamoDB Streams and configure a Lambda event source mapping so item changes invoke the function.",
        "dva-api-gateway-throttling": "Configure API Gateway throttling with rate and burst limits to protect backend integrations from request spikes.",
        "dva-codebuild-buildspec": "Define the install, build, and test command phases in an AWS CodeBuild buildspec file for the managed build project.",
        "dva-eventbridge-schedule-lambda": "Create an EventBridge scheduled rule with the Lambda function as the target for recurring serverless execution.",
    }
    return answers[source_id] if source_id in answers else f"Use {service} for this developer workflow."


def _scenario_purpose(source: dict[str, object], reference_answer: str) -> str:
    if source.get("expected_issue"):
        return str(source["expected_issue"]).strip().rstrip(".")
    if source.get("reasoning_pattern"):
        return str(source["reasoning_pattern"]).strip().rstrip(".")
    return reference_answer.strip().rstrip(".") or "satisfy the developer workflow"


def _artifact_metadata(source: dict[str, object]) -> dict[str, object]:
    if source.get("question_type") != "artifact_review":
        return {}
    return {
        "artifact_type": str(source.get("artifact_type", "")),
        "artifact_language": str(source.get("artifact_language", "")),
        "artifact_body": str(source.get("artifact_body", "")),
        "artifact_context": str(source.get("artifact_context", "")),
        "expected_issue": str(source.get("expected_issue", "")),
    }


if __name__ == "__main__":
    main()
