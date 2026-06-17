#!/usr/bin/env python3
"""Create permitted Developer Associate source-question metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SOURCE_ROWS = [
    {
        "source_id": "dva-lambda-sqs-dlq",
        "source_name": "AWS Documentation: Lambda with SQS event sources",
        "source_url": "https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html",
        "source_license_notes": "AWS public documentation used for topic grounding; question text is self-authored.",
        "allowed_use": "Public AWS documentation concepts summarized locally for calibration.",
        "source_type": "documentation",
        "certification": "AWS Certified Developer - Associate",
        "domain": "Development with AWS Services",
        "task_statement": "Select an event-driven processing pattern that retries failed queue messages and isolates poison messages.",
        "services": ["AWS Lambda", "Amazon SQS"],
        "concepts": ["Lambda event source mapping", "SQS queue", "dead-letter queue", "failed message retry"],
        "difficulty": "Medium",
        "exam_style_notes": "Troubleshooting scenario with an event source, retry behavior, and failure isolation distractors.",
        "distractor_pattern": "Confuse Lambda async destinations, SNS fanout, and CloudWatch alarms with queue failure handling.",
        "reasoning_pattern": "Choose the configuration that preserves messages while preventing repeated failures from blocking processing.",
    },
    {
        "source_id": "dva-api-gateway-lambda-auth",
        "source_name": "AWS Documentation: API Gateway Lambda authorizers",
        "source_url": "https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html",
        "source_license_notes": "AWS public documentation used for topic grounding; question text is self-authored.",
        "allowed_use": "Public AWS documentation concepts summarized locally for calibration.",
        "source_type": "documentation",
        "certification": "AWS Certified Developer - Associate",
        "domain": "Security",
        "task_statement": "Secure an API by running custom authorization logic before a backend Lambda integration is invoked.",
        "services": ["Amazon API Gateway", "AWS Lambda"],
        "concepts": ["API Gateway", "Lambda authorizer", "custom authorization", "backend integration"],
        "difficulty": "Medium",
        "exam_style_notes": "Security configuration scenario asking for the best API access-control mechanism.",
        "distractor_pattern": "Contrast authorizers with WAF rules, security groups, and IAM roles for compute.",
        "reasoning_pattern": "Identify request-time authorization at the API boundary rather than network or instance controls.",
    },
    {
        "source_id": "dva-dynamodb-conditional-write",
        "source_name": "AWS Documentation: DynamoDB condition expressions",
        "source_url": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html",
        "source_license_notes": "AWS public documentation used for topic grounding; question text is self-authored.",
        "allowed_use": "Public AWS documentation concepts summarized locally for calibration.",
        "source_type": "documentation",
        "certification": "AWS Certified Developer - Associate",
        "domain": "Development with AWS Services",
        "task_statement": "Prevent overwriting an item when concurrent writers try to create the same DynamoDB record.",
        "services": ["Amazon DynamoDB"],
        "concepts": ["DynamoDB", "condition expression", "conditional write", "concurrent writes"],
        "difficulty": "Medium",
        "exam_style_notes": "Data consistency scenario requiring a service feature rather than application-side locking.",
        "distractor_pattern": "Confuse conditional writes with scans, global tables, and provisioned throughput changes.",
        "reasoning_pattern": "Use an atomic write condition to enforce uniqueness at the table operation.",
    },
    {
        "source_id": "dva-codepipeline-codebuild",
        "source_name": "AWS Documentation: CodePipeline with CodeBuild",
        "source_url": "https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-CodeBuild.html",
        "source_license_notes": "AWS public documentation used for topic grounding; question text is self-authored.",
        "allowed_use": "Public AWS documentation concepts summarized locally for calibration.",
        "source_type": "documentation",
        "certification": "AWS Certified Developer - Associate",
        "domain": "Deployment",
        "task_statement": "Run repeatable build and test commands as part of an automated application release pipeline.",
        "services": ["AWS CodePipeline", "AWS CodeBuild"],
        "concepts": ["CodePipeline", "CodeBuild", "build stage", "automated release"],
        "difficulty": "Medium",
        "exam_style_notes": "CI/CD workflow scenario with build automation and deployment-stage distractors.",
        "distractor_pattern": "Contrast build actions with CodeDeploy traffic shifting, CloudFormation stacks, and manual scripts.",
        "reasoning_pattern": "Choose the managed build action that integrates into a deployment pipeline.",
    },
    {
        "source_id": "dva-xray-tracing",
        "source_name": "AWS Documentation: AWS X-Ray tracing",
        "source_url": "https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html",
        "source_license_notes": "AWS public documentation used for topic grounding; question text is self-authored.",
        "allowed_use": "Public AWS documentation concepts summarized locally for calibration.",
        "source_type": "documentation",
        "certification": "AWS Certified Developer - Associate",
        "domain": "Troubleshooting and Optimization",
        "task_statement": "Trace requests across distributed application components to find latency and downstream errors.",
        "services": ["AWS X-Ray"],
        "concepts": ["X-Ray", "distributed tracing", "service map", "latency troubleshooting"],
        "difficulty": "Medium",
        "exam_style_notes": "Observability troubleshooting scenario asking for request-level tracing rather than metrics alone.",
        "distractor_pattern": "Distinguish tracing from CloudWatch metrics, CloudTrail audit logs, and Config history.",
        "reasoning_pattern": "Select tracing to follow a request path across services and diagnose latency.",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/original_questions/developer_associate_sources.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(SOURCE_ROWS, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(SOURCE_ROWS)} source question metadata rows to {args.output}.")


if __name__ == "__main__":
    main()
