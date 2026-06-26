from aws_certification_coach.questions import ServiceComparisonQuestionService


def test_service_comparison_service_builds_near_miss_question():
    source = {
        "certification": "Solutions Architect Associate",
        "exam_code": "SAA-C03",
        "domain": "Database",
        "difficulty": "Medium",
        "question": "Explain which AWS service should replicate DynamoDB tables across Regions.",
        "reference_answer": "Use DynamoDB global tables for low-latency multi-Region table replication.",
        "key_concepts": ["DynamoDB", "global tables", "replication", "low latency"],
        "original_multiple_choice": {
            "question": "A workload needs DynamoDB table replication across Regions for low-latency access. What should be used?",
            "options": [
                {"option_id": "A", "text": "Use DynamoDB global tables."},
                {"option_id": "B", "text": "Use an RDS read replica."},
                {"option_id": "C", "text": "Use a CloudWatch dashboard."},
                {"option_id": "D", "text": "Use a local cron job."},
            ],
            "correct_option_ids": ["A"],
            "explanation": "Use DynamoDB global tables for low-latency multi-Region table replication.",
        },
    }

    questions = ServiceComparisonQuestionService().build_questions([source])

    assert len(questions) == 1
    question = questions[0]
    assert question["question_type"] == "service_comparison"
    assert question["best_choice"] == "Use DynamoDB global tables."
    assert question["near_miss_choice"] == "Use an RDS read replica."
    assert question["compared_services"] == ["Use DynamoDB global tables.", "Use an RDS read replica."]
    assert "Compare Use DynamoDB global tables. with Use an RDS read replica." in question["question"]
    assert "tempting but weaker" in question["question"]
    assert question["original_multiple_choice"] == source["original_multiple_choice"]
    assert "replication" in question["tradeoff_concepts"]
    assert question["do_not_claim_explanation"] == [
        "Use DynamoDB global tables is a better option because it satisfies the scenario more directly; Use an RDS read replica is the tempting but weaker alternative."
    ]


def test_service_comparison_service_skips_obviously_weak_distractors():
    source = {
        "certification": "AWS Certified Developer",
        "domain": "Deployment",
        "difficulty": "Medium",
        "key_concepts": ["CodeBuild", "buildspec", "unit tests"],
        "original_multiple_choice": {
            "question": "A build project must run install, build, and test commands. Where should they be defined?",
            "options": [
                {"option_id": "A", "text": "Use a CodeBuild buildspec file."},
                {"option_id": "B", "text": "Create a CloudWatch dashboard."},
                {"option_id": "C", "text": "Run commands manually."},
            ],
            "correct_option_ids": ["A"],
            "explanation": "Use a CodeBuild buildspec file.",
        },
    }

    assert ServiceComparisonQuestionService().build_questions([source]) == []
