"""Generate app-facing AWS certification questions separate from training data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from question_catalog import CERTIFICATION_EXAM_CODES, SERVICE_SPECS, rubric_metadata
except ModuleNotFoundError:  # Imported as scripts.generate_app_question_artifacts in tests.
    from scripts.question_catalog import CERTIFICATION_EXAM_CODES, SERVICE_SPECS, rubric_metadata


APP_VARIANTS = [
    "A team is reviewing an AWS design and needs a solution that can {purpose}. Which AWS service or feature should they choose?",
    "During exam preparation, explain which AWS service or feature is best suited to {purpose}.",
    "An AWS workload must {purpose}. Identify the most appropriate service or feature and explain why.",
    "Which AWS capability best meets a requirement to {purpose}? Explain the selection.",
]

SOURCE_URLS = {
    "IAM roles": "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html",
    "AWS Budgets": "https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html",
    "multiple Availability Zones": "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html",
    "Amazon S3 versioning": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html",
    "S3 lifecycle policies": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html",
    "Amazon RDS Multi-AZ": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html",
    "Amazon RDS read replicas": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html",
    "Amazon DynamoDB": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html",
    "DynamoDB global tables": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html",
    "AWS Lambda": "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
    "Auto Scaling groups": "https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-groups.html",
    "Elastic Load Balancing": "https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html",
    "Amazon CloudFront": "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html",
    "Amazon Route 53": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html",
    "VPC security groups": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html",
    "network ACLs": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html",
    "AWS CloudTrail": "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html",
    "Amazon CloudWatch": "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
    "AWS Config": "https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html",
    "AWS KMS": "https://docs.aws.amazon.com/kms/latest/developerguide/overview.html",
    "AWS Secrets Manager": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html",
    "Amazon SQS": "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html",
    "Amazon SNS": "https://docs.aws.amazon.com/sns/latest/dg/welcome.html",
    "Amazon EventBridge": "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html",
    "AWS Step Functions": "https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html",
    "Amazon API Gateway": "https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html",
    "Amazon EFS": "https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html",
    "Amazon EBS snapshots": "https://docs.aws.amazon.com/ebs/latest/userguide/EBSSnapshots.html",
    "S3 Glacier storage classes": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html",
    "Amazon Redshift": "https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html",
    "AWS Glue": "https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html",
    "Amazon Athena": "https://docs.aws.amazon.com/athena/latest/ug/what-is.html",
    "Amazon Kinesis Data Streams": "https://docs.aws.amazon.com/streams/latest/dev/introduction.html",
    "AWS Organizations": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html",
    "Service Control Policies": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html",
    "AWS Trusted Advisor": "https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html",
    "AWS Well-Architected Tool": "https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html",
    "AWS Backup": "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html",
    "Amazon Cognito": "https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html",
    "AWS WAF": "https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/questions/sample_questions.json")
    parser.add_argument("--count", type=int, default=160)
    args = parser.parse_args()

    questions = _build_app_questions(args.count)
    _write_json(args.output, questions)
    print(f"Generated {len(questions)} app questions into {args.output}.")


def _build_app_questions(count: int) -> list[dict]:
    max_count = len(SERVICE_SPECS) * len(APP_VARIANTS)
    if count > max_count:
        raise ValueError(f"Cannot generate {count} unique app questions from {max_count} source scenarios.")

    questions = []
    for index in range(count):
        spec = SERVICE_SPECS[index % len(SERVICE_SPECS)]
        variant = APP_VARIANTS[index // len(SERVICE_SPECS)]
        service, domain, certification, difficulty, purpose, concepts, distractors = spec
        correct_option = f"Use {service}."
        explanation = f"Use {service} to {purpose}."
        mcq_question = variant.format(purpose=purpose)
        questions.append(
            {
                "certification": certification,
                "exam_code": CERTIFICATION_EXAM_CODES[certification],
                "domain": domain,
                "difficulty": difficulty,
                "question_type": "service_selection",
                "question": f"Explain which AWS service or feature should be used to {purpose}.",
                "reference_answer": explanation,
                "key_concepts": concepts,
                **rubric_metadata(service, concepts, distractors, correct_option, explanation),
                "original_multiple_choice": {
                    "question": mcq_question,
                    "options": [
                        _option("A", correct_option),
                        _option("B", f"Use {distractors[0]}."),
                        _option("C", f"Use {distractors[1]}."),
                        _option("D", f"Use {distractors[2]}."),
                    ],
                    "correct_option_ids": ["A"],
                    "explanation": explanation,
                    "source_name": f"AWS Documentation: {service}",
                    "source_url": SOURCE_URLS[service],
                    "source_license_notes": "AWS documentation was used for topic grounding; this question text is self-authored.",
                },
            }
        )
    return questions


def _option(option_id: str, text: str) -> dict[str, str]:
    payload = {"option_id": option_id, "text": text}
    source_url = documentation_url_for_option(text)
    if source_url:
        payload["source_url"] = source_url
    return payload


def documentation_url_for_option(text: str) -> str:
    normalized = _normalized_option_text(text)
    for service, source_url in SOURCE_URLS.items():
        normalized_service = _normalized_option_text(service)
        if normalized == normalized_service or normalized_service in normalized or normalized in normalized_service:
            return source_url
    return ""


def _normalized_option_text(text: str) -> str:
    value = " ".join(text.casefold().replace(".", "").split())
    return value.removeprefix("use ")


def _write_json(path: str, payload: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
