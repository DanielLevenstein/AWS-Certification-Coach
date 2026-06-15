"""Generate self-authored sample questions and labeled answer examples."""

from __future__ import annotations

import json
from pathlib import Path


SERVICE_SPECS = [
    ("IAM roles", "Security", "Cloud Practitioner", "Easy", "grant temporary credentials to trusted AWS resources without storing long-term access keys", ["IAM", "temporary credentials", "least privilege", "trusted entities"], ["IAM user access keys", "AWS Shield Advanced", "hard-coded credentials"]),
    ("AWS Budgets", "Billing", "Cloud Practitioner", "Easy", "track cost or usage thresholds and send alerts for actual or forecasted spending", ["AWS Budgets", "cost thresholds", "usage thresholds", "alerts"], ["AWS CloudTrail", "AWS Artifact", "Elastic Load Balancing"]),
    ("multiple Availability Zones", "Resilient Architectures", "Solutions Architect Associate", "Medium", "improve high availability and fault tolerance during an Availability Zone impairment", ["Availability Zones", "high availability", "fault tolerance", "load balancing"], ["single Availability Zone deployment", "larger instance", "root volume backups"]),
    ("Amazon S3 versioning", "Storage", "Solutions Architect Associate", "Easy", "preserve, retrieve, and restore previous versions of objects after overwrite or delete events", ["Amazon S3", "versioning", "object recovery", "overwrite protection"], ["S3 Transfer Acceleration", "Amazon EFS", "S3 static website hosting"]),
    ("S3 lifecycle policies", "Storage", "Cloud Practitioner", "Easy", "automatically transition or expire objects based on age and access patterns", ["S3 Lifecycle", "storage classes", "object expiration", "cost optimization"], ["S3 bucket policies", "AWS Organizations", "Amazon GuardDuty"]),
    ("Amazon RDS Multi-AZ", "Database", "Solutions Architect Associate", "Medium", "provide synchronous standby replication and automatic failover for relational databases", ["Amazon RDS", "Multi-AZ", "automatic failover", "standby replica"], ["read replica only", "DynamoDB global table", "manual snapshot"]),
    ("Amazon RDS read replicas", "Database", "Solutions Architect Associate", "Medium", "scale read-heavy database workloads by serving read traffic from replicated database instances", ["Amazon RDS", "read replicas", "read scaling", "replication"], ["Multi-AZ failover", "AWS Backup", "vertical scaling only"]),
    ("Amazon DynamoDB", "Database", "Cloud Practitioner", "Easy", "provide a fully managed NoSQL key-value and document database with low-latency access", ["DynamoDB", "NoSQL", "fully managed", "low latency"], ["Amazon Redshift", "Amazon EFS", "AWS Glue"]),
    ("DynamoDB global tables", "Database", "Solutions Architect Associate", "Medium", "replicate tables across Regions for low-latency multi-Region access and resilience", ["DynamoDB global tables", "multi-Region", "replication", "low latency"], ["DynamoDB local secondary index", "RDS read replica", "S3 replication only"]),
    ("AWS Lambda", "Compute", "Cloud Practitioner", "Easy", "run event-driven code without managing servers and scale per request", ["AWS Lambda", "serverless", "event-driven", "automatic scaling"], ["Amazon EC2 dedicated hosts", "AWS Batch only", "Amazon EBS"]),
    ("Auto Scaling groups", "Compute", "Solutions Architect Associate", "Medium", "adjust EC2 capacity automatically based on demand and health checks", ["Auto Scaling", "EC2", "capacity", "health checks"], ["manual instance launch", "Elastic IP", "AMI copy"]),
    ("Elastic Load Balancing", "Networking", "Cloud Practitioner", "Easy", "distribute traffic across healthy targets to improve availability and scalability", ["Elastic Load Balancing", "traffic distribution", "healthy targets", "scalability"], ["AWS Direct Connect", "Amazon Route 53 only", "Amazon EBS"]),
    ("Amazon CloudFront", "Networking", "Cloud Practitioner", "Easy", "cache and deliver content from edge locations to reduce latency for users", ["CloudFront", "edge locations", "caching", "latency reduction"], ["AWS Transit Gateway", "NAT gateway", "Amazon FSx"]),
    ("Amazon Route 53", "Networking", "Cloud Practitioner", "Easy", "provide scalable DNS routing and health-check-based routing for applications", ["Route 53", "DNS", "routing", "health checks"], ["Amazon CloudWatch Logs", "AWS Config", "Amazon Inspector"]),
    ("VPC security groups", "Networking", "Solutions Architect Associate", "Easy", "act as stateful virtual firewalls controlling inbound and outbound traffic for resources", ["security groups", "stateful", "inbound rules", "outbound rules"], ["network ACL only", "AWS WAF for subnets", "IAM policy"]),
    ("network ACLs", "Networking", "Solutions Architect Associate", "Medium", "provide stateless subnet-level traffic filtering with explicit inbound and outbound rules", ["network ACLs", "stateless", "subnet", "allow and deny rules"], ["security group only", "AWS Shield", "Route 53"]),
    ("AWS CloudTrail", "Security", "Cloud Practitioner", "Easy", "record AWS API activity for auditing, governance, and operational troubleshooting", ["CloudTrail", "API activity", "auditing", "governance"], ["CloudWatch metrics", "AWS Budgets", "Amazon Macie"]),
    ("Amazon CloudWatch", "Operations", "Cloud Practitioner", "Easy", "collect metrics, logs, alarms, and dashboards for monitoring AWS resources", ["CloudWatch", "metrics", "logs", "alarms"], ["AWS Artifact", "AWS Organizations", "AWS Marketplace"]),
    ("AWS Config", "Security", "Solutions Architect Associate", "Medium", "track resource configuration history and evaluate compliance against rules", ["AWS Config", "configuration history", "compliance rules", "resource inventory"], ["CloudTrail only", "Trusted Advisor only", "AWS Shield"]),
    ("AWS KMS", "Security", "Cloud Practitioner", "Easy", "create and manage encryption keys used to protect data in AWS services", ["AWS KMS", "encryption keys", "data protection", "key management"], ["AWS Secrets Manager rotation only", "IAM roles", "AWS WAF"]),
    ("AWS Secrets Manager", "Security", "Solutions Architect Associate", "Medium", "store, retrieve, and rotate application secrets such as database credentials", ["Secrets Manager", "secret rotation", "credentials", "secure retrieval"], ["Parameter Store only", "AWS Certificate Manager", "Amazon Cognito"]),
    ("Amazon SQS", "Integration", "Cloud Practitioner", "Easy", "decouple application components with a managed message queue", ["SQS", "message queue", "decoupling", "asynchronous processing"], ["Amazon SNS only", "Amazon EBS", "AWS CloudFormation"]),
    ("Amazon SNS", "Integration", "Cloud Practitioner", "Easy", "fan out messages to multiple subscribers using a managed pub/sub service", ["SNS", "pub/sub", "fanout", "subscribers"], ["SQS queue polling only", "AWS Batch", "Amazon RDS"]),
    ("Amazon EventBridge", "Integration", "Solutions Architect Associate", "Medium", "route events from AWS services and applications to targets using event buses and rules", ["EventBridge", "event bus", "rules", "event routing"], ["CloudFront", "Amazon EFS", "AWS Artifact"]),
    ("AWS Step Functions", "Application Integration", "Solutions Architect Associate", "Medium", "orchestrate multi-step workflows and coordinate distributed application components", ["Step Functions", "workflow orchestration", "state machine", "coordination"], ["Lambda alone", "Amazon S3 Glacier", "NAT gateway"]),
    ("Amazon API Gateway", "Networking", "Solutions Architect Associate", "Medium", "create, publish, secure, monitor, and throttle APIs for backend services", ["API Gateway", "APIs", "throttling", "backend integration"], ["CloudFront only", "AWS Config", "Amazon EBS"]),
    ("Amazon EFS", "Storage", "Solutions Architect Associate", "Medium", "provide shared elastic file storage that can be mounted by multiple compute resources", ["EFS", "shared file storage", "elastic", "multiple compute resources"], ["Amazon EBS single volume", "S3 object storage only", "DynamoDB"]),
    ("Amazon EBS snapshots", "Storage", "Cloud Practitioner", "Easy", "create point-in-time backups of block storage volumes for recovery or copying", ["EBS snapshots", "point-in-time backup", "block storage", "recovery"], ["S3 lifecycle", "CloudTrail event", "Route 53 health check"]),
    ("S3 Glacier storage classes", "Storage", "Cloud Practitioner", "Easy", "store rarely accessed archival data at lower cost with retrieval-time tradeoffs", ["S3 Glacier", "archive", "low cost", "retrieval time"], ["S3 Standard only", "Amazon EFS", "Amazon ElastiCache"]),
    ("Amazon Redshift", "Analytics", "Cloud Practitioner", "Easy", "run analytical queries against a managed petabyte-scale data warehouse", ["Redshift", "data warehouse", "analytics", "SQL queries"], ["DynamoDB", "Amazon SQS", "AWS Lambda"]),
    ("AWS Glue", "Analytics", "Cloud Practitioner", "Easy", "perform serverless data integration, cataloging, and ETL jobs", ["AWS Glue", "ETL", "data catalog", "serverless"], ["AWS Config", "Amazon Route 53", "AWS Shield"]),
    ("Amazon Athena", "Analytics", "Cloud Practitioner", "Easy", "query data in Amazon S3 using SQL without managing servers", ["Athena", "SQL", "Amazon S3", "serverless queries"], ["Amazon RDS", "Amazon EBS", "AWS WAF"]),
    ("Amazon Kinesis Data Streams", "Analytics", "Solutions Architect Associate", "Medium", "ingest and process real-time streaming data at scale", ["Kinesis Data Streams", "real-time", "streaming data", "shards"], ["AWS Glue crawler", "S3 Glacier", "CloudTrail Lake only"]),
    ("AWS Organizations", "Governance", "Cloud Practitioner", "Easy", "centrally manage multiple AWS accounts and apply service control policies", ["AWS Organizations", "multiple accounts", "SCPs", "central management"], ["IAM groups only", "AWS Budgets only", "Amazon Cognito"]),
    ("Service Control Policies", "Governance", "Solutions Architect Associate", "Medium", "set maximum available permissions across accounts in an AWS Organization", ["SCPs", "permission guardrails", "AWS Organizations", "accounts"], ["resource policies only", "security groups", "CloudWatch alarms"]),
    ("AWS Trusted Advisor", "Governance", "Cloud Practitioner", "Easy", "provide recommendations for cost optimization, security, fault tolerance, performance, and service limits", ["Trusted Advisor", "recommendations", "cost optimization", "service limits"], ["CloudTrail", "AWS Glue", "Amazon SQS"]),
    ("AWS Well-Architected Tool", "Governance", "Cloud Practitioner", "Easy", "review workloads against AWS best practices and identify improvement opportunities", ["Well-Architected Tool", "best practices", "workload review", "improvements"], ["AWS Artifact", "AWS Backup only", "Route 53"]),
    ("AWS Backup", "Storage", "Solutions Architect Associate", "Medium", "centralize and automate backup policies across supported AWS services", ["AWS Backup", "centralized backups", "backup policies", "automation"], ["CloudFront", "Amazon SNS", "AWS Config only"]),
    ("Amazon Cognito", "Security", "Solutions Architect Associate", "Medium", "add user sign-up, sign-in, and identity management to applications", ["Cognito", "user authentication", "identity management", "sign-in"], ["IAM role for EC2", "AWS KMS", "CloudTrail"]),
    ("AWS WAF", "Security", "Cloud Practitioner", "Easy", "protect web applications from common web exploits using rules", ["AWS WAF", "web application", "rules", "common exploits"], ["security groups only", "Amazon Inspector", "AWS Budgets"]),
]


VARIANTS = [
    "A team needs to choose the AWS capability that will {purpose}. Which option should they use?",
    "A workload requirement says the solution must {purpose}. Which AWS service or feature best fits?",
    "An architect is designing a solution to {purpose}. Which choice is most appropriate?",
]


def main() -> None:
    training_artifacts = _build_artifacts(start_index=0, count=100, question_prefix="AWS-GEN")
    holdout_artifacts = _build_artifacts(start_index=100, count=100, question_prefix="AWS-HOLDOUT")

    _write_json("data/generated/questions_with_answers_generated.json", training_artifacts["questions"])
    _write_json("data/verification/questions_with_answers_holdout.json", holdout_artifacts["questions"])
    print(
        "Generated "
        f"{len(training_artifacts['questions'])} training questions, "
        f"{sum(len(question['generated_answers']) for question in training_artifacts['questions'])} graded training answers, "
        f"{len(holdout_artifacts['questions'])} holdout questions, "
        f"{sum(len(question['generated_answers']) for question in holdout_artifacts['questions'])} graded holdout answers."
    )


def _build_artifacts(start_index: int, count: int, question_prefix: str) -> dict[str, list[dict]]:
    questions = []
    for offset in range(count):
        index = start_index + offset
        service, domain, certification, difficulty, purpose, concepts, distractors = SERVICE_SPECS[index % len(SERVICE_SPECS)]
        variant = VARIANTS[index % len(VARIANTS)]
        question_id = f"AWS-GEN-{index + 1:03d}"
        if question_prefix != "AWS-GEN":
            question_id = f"{question_prefix}-{offset + 1:03d}"
        mcq_question = variant.format(purpose=purpose)
        explanation = f"Use {service} to {purpose}."
        correct_option = f"Use {service}."
        original_multiple_choice = {
            "question": mcq_question,
            "options": [
                {"option_id": "A", "text": correct_option},
                {"option_id": "B", "text": f"Use {distractors[0]}."},
                {"option_id": "C", "text": f"Use {distractors[1]}."},
                {"option_id": "D", "text": f"Use {distractors[2]}."},
            ],
            "correct_option_ids": ["A"],
            "explanation": explanation,
            "source_name": "Generated self-authored exam-style sample",
            "source_url": "",
            "source_license_notes": "Generated for this project; not copied from an official exam or practice test.",
        }
        question = {
            "question_id": question_id,
            "certification": certification,
            "domain": domain,
            "difficulty": difficulty,
            "question": f"Explain which AWS service or feature should be used to {purpose}.",
            "reference_answer": explanation,
            "key_concepts": concepts,
            "original_multiple_choice": original_multiple_choice,
            "generated_answers": _generated_answers(
                question_id,
                service,
                purpose,
                concepts,
                distractors,
                explanation,
                correct_option,
                mcq_question,
            ),
        }
        questions.append(question)
    return {"questions": questions}


def _generated_answers(question_id, service, purpose, concepts, distractors, explanation, correct_option, question_text):
    answers = [
        (correct_option, "A", "generated_exact_answer", 1.0),
        (explanation, "A", "generated_complete_answer", 1.0),
        (f"{service} is appropriate because it helps {purpose}.", "A", "generated_complete_paraphrase", 1.0),
        (_drop_every_nth_word(explanation, 4), "B", "generated_shortened_answer", 0.85),
        (f"The best choice is {service}; key ideas include {', '.join(concepts[:2])}.", "B", "generated_key_concepts", 0.75),
        (_rating_75_answer(service, concepts, 0), "B", "generated_75_percent_answer", 0.75),
        (_rating_75_answer(service, concepts, 1), "B", "generated_75_percent_paraphrase", 0.75),
        (_rating_50_answer(service, concepts, 0), "C", "generated_50_percent_answer", 0.50),
        (_rating_50_answer(service, concepts, 1), "D", "generated_50_percent_paraphrase", 0.50),
        (_rating_25_answer(question_text), "D", "generated_25_percent_answer", 0.25),
        (f"Use {distractors[0]}.", "F", "generated_distractor", 0.0),
        (f"Use {distractors[1]}.", "F", "generated_distractor", 0.0),
        (f"Use {distractors[2]}.", "F", "generated_distractor", 0.0),
    ]
    return [
        {
            "question_id": question_id,
            "answer": answer,
            "rating": rating,
            "intended_coverage": intended_coverage,
            "source": source,
        }
        for answer, rating, source, intended_coverage in answers
    ]


def _rating_75_answer(service_name: str, concepts: list[str], index: int) -> str:
    if "IAM" in service_name or any("temporary credentials" == concept for concept in concepts):
        return [
            "Assume a role with S3 bucket permission.",
            "Use a role for S3 access instead of putting keys on the instance.",
        ][index % 2]
    supporting_concepts = [concept for concept in concepts if concept.casefold() not in service_name.casefold()]
    if index % 2 == 1 and supporting_concepts:
        return f"{service_name} handles this; mention {supporting_concepts[0]}."
    if supporting_concepts:
        return f"Use {service_name} and mention {supporting_concepts[0]}."
    return f"Use {service_name} for the requirement."


def _rating_50_answer(service_name: str, concepts: list[str], index: int) -> str:
    supporting_concepts = [concept for concept in concepts if concept.casefold() not in service_name.casefold()]
    concept = supporting_concepts[index % len(supporting_concepts)] if supporting_concepts else "an AWS feature"
    if index % 2 == 1:
        return f"Use a service related to {concept}."
    return f"This is generally about {concept}, but the specific AWS service is unclear."


def _rating_25_answer(question_text: str) -> str:
    lowered = question_text.casefold()
    if "cost" in lowered or "spend" in lowered or "budget" in lowered:
        return "Set up a cost alert."
    if "available" in lowered or "fail" in lowered or "zone" in lowered:
        return "Make the application more redundant."
    if "access" in lowered or "permission" in lowered or "security" in lowered:
        return "Use permissions for the resource."
    return "Use an AWS managed service for this requirement."


def _drop_every_nth_word(value: str, n: int) -> str:
    words = value.split()
    kept = [word for index, word in enumerate(words, start=1) if index % n != 0]
    return " ".join(kept) if kept else value


def _question_number(question_id: str) -> int:
    digits = "".join(character for character in question_id if character.isdigit())
    return int(digits or "0")


def _write_json(path, payload) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
