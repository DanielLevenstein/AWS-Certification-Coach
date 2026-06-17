#!/usr/bin/env python3
"""Generate self-authored Developer Associate freeform questions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aws_certification_coach.question_fidelity.model import QuestionFidelityModel


QUESTION_TEMPLATES = {
    "dva-lambda-sqs-dlq": "A Lambda function processes messages from an SQS queue. A few messages repeatedly fail and delay later processing. Which configuration should the developer use to isolate failed messages while allowing successful messages to continue?",
    "dva-api-gateway-lambda-auth": "A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?",
    "dva-dynamodb-conditional-write": "Two application instances may try to create the same DynamoDB item at the same time. Which DynamoDB write approach should the developer use to prevent replacing an existing item?",
    "dva-codepipeline-codebuild": "A development team wants its release pipeline to compile code and run unit tests automatically before deployment. Which AWS service should be added as the build action?",
    "dva-xray-tracing": "A serverless application has intermittent latency across several downstream calls. Which AWS service should the developer use to trace each request through the distributed workflow?",
}

DISTRACTORS = {
    "dva-lambda-sqs-dlq": ["Configure an SNS topic subscription.", "Add a CloudWatch alarm only.", "Use Lambda provisioned concurrency."],
    "dva-api-gateway-lambda-auth": ["Attach an EC2 security group.", "Create an AWS WAF rate-based rule only.", "Store the token in AWS Secrets Manager."],
    "dva-dynamodb-conditional-write": ["Run a table scan before each write.", "Increase write capacity units.", "Replicate the table with global tables."],
    "dva-codepipeline-codebuild": ["Use CodeDeploy lifecycle hooks only.", "Run commands manually on an EC2 instance.", "Create a CloudWatch dashboard."],
    "dva-xray-tracing": ["Use CloudTrail event history.", "Use AWS Config resource history.", "Increase Lambda memory without tracing."],
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
    questions: list[dict[str, object]] = []
    for source in sources:
        source_id = str(source["source_id"])
        service = str(source["services"][0])
        concepts = [str(concept) for concept in source["concepts"]]
        question_text = QUESTION_TEMPLATES[source_id]
        reference_answer = _reference_answer(source_id, service)
        options = [
            {"option_id": "A", "text": reference_answer},
            *[
                {"option_id": option_id, "text": text}
                for option_id, text in zip(["B", "C", "D"], DISTRACTORS[source_id], strict=True)
            ],
        ]
        row = {
            "certification": source["certification"],
            "domain": source["domain"],
            "difficulty": source["difficulty"],
            "question": question_text,
            "reference_answer": reference_answer,
            "key_concepts": concepts,
            "original_multiple_choice": {
                "question": f"{question_text} Choose the best answer.",
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
        row["question_fidelity"] = model.score(source, row).__dict__
        questions.append(row)
    return questions


def _reference_answer(source_id: str, service: str) -> str:
    answers = {
        "dva-lambda-sqs-dlq": "Configure the Lambda event source mapping with an SQS dead-letter queue so failed messages can be isolated after retries.",
        "dva-api-gateway-lambda-auth": "Use an API Gateway Lambda authorizer to run custom authorization logic before invoking the backend Lambda integration.",
        "dva-dynamodb-conditional-write": "Use a DynamoDB conditional write with a condition expression such as attribute_not_exists to avoid overwriting an existing item.",
        "dva-codepipeline-codebuild": "Add AWS CodeBuild as a CodePipeline build stage to compile the application and run tests automatically.",
        "dva-xray-tracing": "Use AWS X-Ray distributed tracing and service maps to follow requests and identify latency across downstream calls.",
    }
    return answers[source_id] if source_id in answers else f"Use {service} for this developer workflow."


if __name__ == "__main__":
    main()
