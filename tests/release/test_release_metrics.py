from pathlib import Path
import struct
import subprocess

from aws_certification_coach.release_metrics.complexity import measure_complexity
from aws_certification_coach.release_metrics.question_coverage import (
    measure_question_coverage,
    plot_question_coverage_artifacts,
)
from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.model_evaluation.semantic_similarity import (
    LEGACY_ACCEPTED_GRADES,
    evaluate_semantic_curated_answers,
    semantic_similarity_score,
)
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.ratings import score_to_letter
from aws_certification_coach.training.features import AnswerFeatureExtractor, correct_answer_text
from scripts.release_metrics import render_release_metrics, update_release_notes
from scripts.semantic_similarity_evaluation import (
    plot_grade_distribution,
    plot_grade_band_metrics,
    plot_per_grade_metrics,
    plot_semantic_accuracy,
)
from scripts.combine_release_charts import combine_accuracy_charts, combine_question_coverage_charts
from scripts.combine_curated_training_data import combine_curated_training_data


STRUCTURED_QUESTIONS = JsonQuestionRepository(
    Path(__file__).resolve().parents[2] / "config" / "data" / "structured_answer_training_data.json"
).all()


def test_legacy_semantic_acceptance_definition_remains_frozen():
    assert LEGACY_ACCEPTED_GRADES == {"A", "B", "C", "D"}


def _structured_question(fragment: str) -> Question:
    matches = [question for question in STRUCTURED_QUESTIONS if fragment.casefold() in question.question.casefold()]
    assert len(matches) == 1, f"Expected one structured question matching {fragment!r}, found {len(matches)}"
    return matches[0]


def test_complexity_reports_branching_functions(tmp_path: Path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "sample.py").write_text(
        "def choose(value):\n    if value:\n        return 1\n    return 0\n",
        encoding="utf-8",
    )

    metrics = measure_complexity(source)

    assert metrics["function_count"] == 1
    assert metrics["maximum_complexity"] == 2


def test_semantic_accuracy_chart_writes_png(tmp_path: Path):
    output = tmp_path / "semantic_accuracy.png"

    plot_semantic_accuracy(
        {
            "semantic_grade_accuracy": 0.8,
            "semantic_precision": 0.9,
            "semantic_recall": 0.75,
            "semantic_exact_letter_accuracy": 0.64,
        },
        output,
    )

    assert output.read_bytes().startswith(b"\x89PNG")


def test_semantic_accuracy_chart_includes_within_one_letter_metric(tmp_path: Path):
    output = tmp_path / "semantic_accuracy.png"

    plot_semantic_accuracy(
        {
            "semantic_grade_accuracy": 0.8,
            "semantic_precision": 0.9,
            "semantic_recall": 0.75,
            "semantic_exact_letter_accuracy": 0.64,
            "semantic_within_one_letter_accuracy": 0.92,
        },
        output,
    )

    assert output.read_bytes().startswith(b"\x89PNG")


def test_per_grade_chart_includes_semantic_precision_and_recall(tmp_path: Path):
    output = tmp_path / "per_grade_metrics.png"
    evaluation = {
        "per_grade": {
            grade: {"precision": precision, "recall": recall}
            for grade, precision, recall in zip(
                ("A", "B", "C", "D", "F"),
                (0.92, 0.86, 0.87, 0.89, 1.0),
                (0.88, 0.76, 0.64, 0.71, 0.95),
                strict=True,
            )
        }
    }

    plot_per_grade_metrics(evaluation, output)

    assert output.read_bytes().startswith(b"\x89PNG")


def test_per_grade_chart_renders_precision_below_guardrail(tmp_path: Path):
    output = tmp_path / "per_grade_metrics.png"
    evaluation = {
        "per_grade": {
            grade: {"precision": precision, "recall": 0.9}
            for grade, precision in zip(
                ("A", "B", "C", "D", "F"),
                (0.92, 0.86, 0.69, 0.89, 1.0),
                strict=True,
            )
        }
    }

    plot_per_grade_metrics(evaluation, output)

    assert output.read_bytes().startswith(b"\x89PNG")


def test_grade_band_chart_uses_exclusive_a_bc_df_bands(tmp_path: Path):
    output = tmp_path / "grade_band_metrics.png"
    evaluation = {
        "per_grade_band": {
            "A": {"precision": 0.88, "recall": 0.91},
            "BC": {"precision": 0.86, "recall": 0.64},
            "DF": {"precision": 0.93, "recall": 0.88},
        }
    }

    plot_grade_band_metrics(evaluation, output)

    assert output.read_bytes().startswith(b"\x89PNG")


def test_grade_band_chart_renders_precision_below_guardrail(tmp_path: Path):
    output = tmp_path / "grade_band_metrics.png"
    evaluation = {
        "per_grade_band": {
            "A": {"precision": 0.88, "recall": 0.91},
            "BC": {"precision": 0.84, "recall": 0.64},
            "DF": {"precision": 0.93, "recall": 0.88},
        }
    }

    plot_grade_band_metrics(evaluation, output)

    assert output.read_bytes().startswith(b"\x89PNG")


def test_grade_distribution_chart_counts_expected_letters(tmp_path: Path):
    output = tmp_path / "grade_distribution_metrics.png"
    evaluation = {
        "per_grade": {
            "A": {"support": 10},
            "B": {"support": 4},
            "C": {"support": 3},
            "D": {"support": 209},
            "F": {"support": 11},
        }
    }

    plot_grade_distribution(evaluation, output)

    assert output.read_bytes().startswith(b"\x89PNG")


def test_question_coverage_metrics_and_chart_write_png(tmp_path: Path):
    rows = [
        {
            "certification": "AWS Certified Developer",
            "domain": "Development with AWS Services",
            "difficulty": "Medium",
            "question_type": "service_comparison",
            "question_category": "integration_workflows",
            "question": "Compare Lambda with SQS for this retry scenario.",
            "key_concepts": ["Lambda", "SQS", "dead-letter queue"],
            "original_multiple_choice": {"source_name": "AWS Documentation: Lambda"},
        },
        {
            "certification": "AWS Certified Developer",
            "domain": "Development with AWS Services",
            "difficulty": "Medium",
            "question_category": "integration_workflows",
            "question": "Which service should run code when a schedule fires?",
            "key_concepts": ["Lambda", "EventBridge"],
            "original_multiple_choice": {"source_name": "AWS Documentation: EventBridge"},
        },
        {
            "certification": "Solutions Architect Associate",
            "domain": "Storage",
            "difficulty": "Easy",
            "question_category": "cost_tradeoff",
            "question": "Which lifecycle policy configuration should transition older objects?",
            "key_concepts": ["Amazon S3", "replication"],
            "original_multiple_choice": {"source_name": "AWS Documentation: S3"},
        },
    ]
    output = tmp_path / "question_coverage.png"

    metrics = measure_question_coverage(rows)
    outputs = plot_question_coverage_artifacts(metrics, tmp_path)

    assert metrics["question_count"] == 3
    assert metrics["domain_count"] == 2
    assert metrics["concept_count"] == 6
    assert metrics["question_category_count"] == 2
    assert {"name": "integration_workflows", "count": 2} in metrics["question_categories"]
    assert {"name": "cost_tradeoff", "count": 1} in metrics["question_categories"]
    assert set(outputs) == {"domain", "question_category", "certification"}
    for output in outputs.values():
        assert output.read_bytes().startswith(b"\x89PNG")
        width, height = _png_dimensions(output)
        assert width >= 1500
        assert height >= 1000


def test_question_coverage_metrics_exclude_disabled_artifact_review_questions(monkeypatch):
    rows = [
        {
            "certification": "AWS Certified Developer",
            "domain": "Development with AWS Services",
            "difficulty": "Medium",
            "question_type": "service_selection",
            "question_category": "integration_workflows",
            "question": "Which service should run code when a schedule fires?",
            "key_concepts": ["Lambda", "EventBridge"],
        },
        {
            "certification": "AWS Certified Developer",
            "domain": "Security",
            "difficulty": "Medium",
            "question_type": "artifact_review",
            "question_category": "security_identity",
            "question": "Review this policy.",
            "key_concepts": ["IAM policy", "least privilege"],
        },
    ]

    monkeypatch.delenv("SHOW_ARTIFACT_REVIEW", raising=False)
    metrics = measure_question_coverage(rows)

    assert metrics["question_count"] == 1
    assert {"name": "security_identity", "count": 1} not in metrics["question_categories"]

    monkeypatch.setenv("SHOW_ARTIFACT_REVIEW", "1")
    metrics = measure_question_coverage(rows)

    assert metrics["question_count"] == 2
    assert {"name": "security_identity", "count": 1} in metrics["question_categories"]


def test_question_coverage_shell_wrapper_accepts_release_tag(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    latest_outputs = [
        project_root / "release" / "question_domain_coverage.png",
        project_root / "release" / "question_intent_coverage.png",
        project_root / "release" / "question_certification_coverage.png",
    ]
    result = subprocess.run(
        ["./generate_question_coverage.sh", "test-build"],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "release/question_domain_coverage.png" in result.stdout
    assert "release/question_intent_coverage.png" in result.stdout
    assert "release/question_certification_coverage.png" in result.stdout
    for latest_output in latest_outputs:
        assert latest_output.exists()


def test_combined_release_charts_split_accuracy_from_question_coverage(tmp_path: Path):
    paths = {}
    for index, title in enumerate([
        "Semantic Similarity",
        "Certification Split",
        "Per-Grade Precision & Recall",
        "Grade Bands",
        "Domain Coverage",
        "Question Category",
    ]):
        path = tmp_path / f"chart_{index}.png"
        _write_sample_chart(path, title)
        paths[title] = path
    accuracy_output = tmp_path / "accuracy_metrics_chart.png"
    coverage_output = tmp_path / "question_coverage_metrics_chart.png"

    combine_accuracy_charts(
        [
            (title, paths[title])
            for title in ("Semantic Similarity", "Grade Bands", "Per-Grade Precision & Recall")
        ],
        accuracy_output,
    )
    combine_question_coverage_charts(
        [(title, paths[title]) for title in ("Certification Split", "Domain Coverage", "Question Category")],
        coverage_output,
    )

    assert accuracy_output.read_bytes().startswith(b"\x89PNG")
    assert coverage_output.read_bytes().startswith(b"\x89PNG")
    accuracy_width, accuracy_height = _png_dimensions(accuracy_output)
    coverage_width, coverage_height = _png_dimensions(coverage_output)
    assert accuracy_width > accuracy_height
    assert coverage_width > coverage_height


def _write_sample_chart(path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(4, 3))
    axis.bar(["A", "B"], [1, 2])
    axis.set_title(title)
    figure.savefig(path, dpi=80)
    plt.close(figure)


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as image_file:
        header = image_file.read(24)
    if not header.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a PNG file: {path}")
    return struct.unpack(">II", header[16:24])

def test_release_metrics_tracks_curated_and_per_grade_accuracy(tmp_path: Path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "semantic_similarity.json").write_text(
        '{"semantic_grade_accuracy": 0.8, "semantic_precision": 0.9, "semantic_recall": 0.75, '
        '"semantic_exact_letter_accuracy": 0.64, "semantic_within_one_letter_accuracy": 0.76, '
        '"semantic_example_count": 25, "per_grade": {'
        '"A": {"precision": 0.9, "recall": 0.8, "f1": 0.847, "support": 10}, '
        '"B": {"precision": 0.8, "recall": 0.7, "f1": 0.747, "support": 9}, '
        '"C": {"precision": 0.7, "recall": 0.6, "f1": 0.646, "support": 8}, '
        '"D": {"precision": 0.6, "recall": 0.5, "f1": 0.545, "support": 7}, '
        '"F": {"precision": 1.0, "recall": 0.9, "f1": 0.947, "support": 6}'
        '}, "per_grade_band": {'
        '"A": {"precision": 0.85, "recall": 0.9, "f1": 0.874, "support": 10}, '
        '"BC": {"precision": 0.7, "recall": 0.6, "f1": 0.646, "support": 17}, '
        '"DF": {"precision": 0.92, "recall": 0.88, "f1": 0.9, "support": 13}'
        '}}',
        encoding="utf-8",
    )
    (metrics_dir / "knowledge_base.json").write_text(
        '{"schema_version": 2, "file_size_bytes": 12000, "syntax_alias_count": 18, '
        '"service_count": 42, "concept_count": 161}',
        encoding="utf-8",
    )

    markdown = render_release_metrics(metrics_dir, release_label="v2.5")

    assert "| v2.5 | 80.00% | 90.00% | 75.00% | 64.00% | 76.00% | N/A |" in markdown
    assert "## Per Grade Metrics" in markdown
    assert "## Grade Band Metrics" in markdown
    assert "![Grade distribution by letter]" not in markdown
    assert "| Metric | A | BC | DF |" in markdown
    assert "| Precision | 85.00% | 70.00% | 92.00% |" in markdown
    assert "| Precision | 90.00% | 80.00% | 70.00% | 60.00% | 100.00% |" in markdown
    assert "| Support | 10 | 9 | 8 | 7 | 6 |" in markdown
    assert "Answer evaluator: `semantic_similarity`" in markdown
    assert "Knowledge base schema version: `2`" in markdown
    assert "Knowledge base syntax alias count: `18`" in markdown
    assert "Knowledge base service count: `42`" in markdown
    assert "Knowledge base concept count: `161`" in markdown

def test_release_metrics_can_mark_exact_letter_strict_grading(tmp_path: Path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "semantic_similarity.json").write_text(
        '{"semantic_grade_accuracy": 0.8, "semantic_precision": 0.9, "semantic_recall": 0.75, '
        '"semantic_exact_letter_accuracy": 0.64, "semantic_example_count": 25}',
        encoding="utf-8",
    )

    markdown = render_release_metrics(metrics_dir, release_label="v2.3.1", strict_grading=True)

    assert "Exact Letter Accuracy" in markdown
    assert "Within 1 Letter" in markdown

def test_release_metrics_updates_generated_release_notes_block(tmp_path: Path):
    release_notes = tmp_path / "RELEASE_NOTES.md"
    release_notes.write_text("# Release Notes\n\nExisting notes.\n", encoding="utf-8")
    markdown = "# Release Metrics\n\n| Release | Semantic Accuracy |\n|:--------|------------------:|\n| v1 | 96.00% |\n"

    update_release_notes(release_notes, markdown)
    update_release_notes(release_notes, markdown.replace("96.00%", "97.00%"))

    content = release_notes.read_text(encoding="utf-8")
    assert content.count("<!-- release-metrics:start -->") == 1
    assert "Existing notes." in content
    assert "97.00%" in content
    assert "96.00%" not in content

def test_semantic_similarity_recognizes_aliases_and_concepts():
    question = _structured_question("manages encryption keys")

    assert semantic_similarity_score(question, "KMS manages encryption keys.") >= 80
    assert semantic_similarity_score(question, "Use Amazon S3.") < 60


def test_semantic_similarity_requires_reasoning_for_a_grade():
    question = _structured_question("manages encryption keys")

    assert 80 <= semantic_similarity_score(question, "The correct service is AWS KMS.") < 90
    assert semantic_similarity_score(question, "AWS KMS manages encryption keys.") >= 90
    assert semantic_similarity_score(question, "aws KMS manages encryption keys.") >= 90
    assert semantic_similarity_score(question, "aWS KMS manages encryption keys.") >= 90
    assert semantic_similarity_score(question, "KMS") < 90


def test_semantic_similarity_uses_syntax_alias_table_for_service_names():
    cloudtrail_question = _structured_question("records AWS API activity")
    codebuild_question = _structured_question("managed build project")

    assert semantic_similarity_score(cloudtrail_question, "AWS Cloud trail records API activity for auditing.") >= 90
    assert 80 <= semantic_similarity_score(cloudtrail_question, "Use AWS CloudTrail.") < 90
    assert semantic_similarity_score(codebuild_question, "AWS Code Build") >= 80

def test_semantic_similarity_uses_acceptable_answers_as_correct_evidence():
    question = _structured_question("managed build project")

    assert semantic_similarity_score(question, "AWS Code Build") >= 90

def test_semantic_similarity_recognizes_strong_concept_prose_answers():
    project_root = Path(__file__).resolve().parents[2]
    questions = JsonQuestionRepository(project_root / "data" / "questions" / "sample_questions.json").all()
    secondary_index_question = next(
        question
        for question in questions
        if "fast lookups by order status" in question.question
    )
    lifecycle_question = next(
        question
        for question in questions
        if "automatically transition or expire objects" in question.question
    )
    multi_az_question = next(
        question
        for question in questions
        if "synchronous standby replication" in question.question
    )

    assert semantic_similarity_score(
        secondary_index_question,
        "The user should add a second database index for order status.",
    ) >= 90
    assert semantic_similarity_score(
        lifecycle_question,
        "S3 lifestyle policies are used to expire objects based on age and access patterns",
    ) >= 90
    assert semantic_similarity_score(
        multi_az_question,
        "Synchronous standby replication with automatic failover is provided by using multi AZ deployment with failover.",
    ) >= 90

def test_semantic_similarity_recognizes_artifact_resource_path_answer():
    project_root = Path(__file__).resolve().parents[2]
    questions = JsonQuestionRepository(project_root / "data" / "questions" / "sample_questions.json").all()
    question = next(
        question
        for question in questions
        if "Lambda execution role" in question.question
    )

    assert semantic_similarity_score(
        question,
        'Change resource to \n"Resource": "s3://example-bucket/reports/*"',
    ) >= 90

def test_semantic_similarity_recognizes_budget_cost_center_alias():
    question = _structured_question("track cost or usage thresholds")

    assert 80 <= semantic_similarity_score(question, "AWS Cost Center") < 90

def test_semantic_similarity_does_not_treat_long_acceptable_answer_words_as_service_aliases():
    question = _structured_question("track resource configuration history")

    assert semantic_similarity_score(question, "AWS Compliance Manager") < 60

def test_semantic_accuracy_uses_grade_bands_and_reports_exact_letter_match(tmp_path: Path):
    question = _structured_question("manages encryption keys")
    curated = tmp_path / "curated.json"
    curated.write_text(
        (
            '[{"question": "Which service manages encryption keys?", '
            '"reference_answer": "Use AWS KMS to create and manage encryption keys.", '
            '"answer_given": "KMS", '
            '"correct_rating": "A", "rating_given": "A"}]'
        ),
        encoding="utf-8",
    )

    metrics = evaluate_semantic_curated_answers(curated, [question])

    assert metrics["semantic_grade_accuracy"] == 1
    assert metrics["semantic_matching_grade_bands"] == 1
    assert metrics["semantic_exact_letter_accuracy"] == 0

def test_curated_semantic_metrics_keep_grade_a_precision_high():
    project_root = Path(__file__).resolve().parents[2]
    questions = JsonQuestionRepository(project_root / "data" / "questions" / "sample_questions.json").all()

    metrics = evaluate_semantic_curated_answers(
        project_root / "data" / "curated" / "curated_training_data.json",
        questions,
    )

    assert metrics["per_grade_band"]["A"]["precision"] >= 0.9

def test_config_curated_semantic_metrics_keep_per_grade_precision_stable(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    questions = JsonQuestionRepository(project_root / "data" / "questions" / "sample_questions.json").all()
    curated = tmp_path / "curated_training_data.json"
    combine_curated_training_data(project_root / "config" / "data", curated)

    metrics = evaluate_semantic_curated_answers(
        curated,
        questions,
    )

    assert all(metrics["per_grade"][grade]["precision"] >= 0.8 for grade in "ABCDF")

def test_semantic_accuracy_skips_conflicting_duplicate_feedback(tmp_path: Path):
    question = _structured_question("manages encryption keys")
    curated = tmp_path / "curated.json"
    curated.write_text(
        """
        [
          {
            "question": "Which service manages encryption keys?",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "answer_given": "Ambiguous answer",
            "correct_rating": "C",
            "rating_given": "F"
          },
          {
            "question": "Which service manages encryption keys?",
            "reference_answer": "Use AWS KMS to create and manage encryption keys.",
            "answer_given": "Ambiguous answer",
            "correct_rating": "F",
            "rating_given": "C"
          }
        ]
        """,
        encoding="utf-8",
    )

    metrics = evaluate_semantic_curated_answers(curated, [question])

    assert metrics["semantic_example_count"] == 0
    assert metrics["semantic_skipped_conflicting_examples"] == 2
    assert metrics["semantic_conflicting_feedback_groups"][0]["labels"] == ["C", "F"]

def test_semantic_similarity_awards_adjacent_partial_credit_without_family_token_false_positive():
    secrets_question = _structured_question("database passwords")
    s3_question = _structured_question("transitions or expires S3 objects")

    assert score_to_letter(semantic_similarity_score(secrets_question, "AWS KMS Keys")) == "D"
    assert semantic_similarity_score(s3_question, "S3 version tracking") < 60

def test_semantic_similarity_caps_question_rephrases_without_answer_detail():
    question = _structured_question("custom token validation")

    assert semantic_similarity_score(
        question,
        "Which API Gateway feature should be used to run token validation on requests?",
    ) < 80
    assert semantic_similarity_score(
        question,
        "This question is asking the learner to identify which API Gateway feature should run token validation on requests.",
    ) < 80
    assert semantic_similarity_score(question, "Use an API Gateway Lambda authorizer.") >= 80

def test_semantic_similarity_caps_hedged_and_ambiguous_service_mentions():
    api_question = _structured_question("custom token validation")
    sqs_question = _structured_question("another worker does not immediately receive")

    assert semantic_similarity_score(
        api_question,
        "I don't know. AWS API Gateway routes requests, but I would be guessing.",
    ) < 70
    assert semantic_similarity_score(
        api_question,
        "Use API Gateway or AWS WAF for token validation.",
    ) < 80
    assert semantic_similarity_score(sqs_question, "SQS FILO queue") < 80


def test_semantic_similarity_caps_concept_only_answers_without_service_name():
    project_root = Path(__file__).resolve().parents[2]
    questions = JsonQuestionRepository(project_root / "data" / "questions" / "sample_questions.json").all()
    question = next(
        question
        for question in questions
        if "replicate tables across Regions" in question.question
    )

    assert score_to_letter(semantic_similarity_score(question, "Global Database Tables")) == "C"


def test_semantic_similarity_does_not_cap_correct_requirement_or_wording():
    question = _structured_question("track cost or usage thresholds")

    assert score_to_letter(
        semantic_similarity_score(
            question,
            "Use AWS Budgets to set alerts when production services exceed cost or usage thresholds.",
        )
    ) == "A"

def test_correct_answer_text_uses_multiple_choice_value_without_answer_cue():
    question = Question(
        schema_version=1,
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Which service manages encryption keys?",
        reference_answer="Use AWS KMS to create and manage encryption keys.",
        key_concepts=["AWS KMS"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which service manages encryption keys?",
            options=[
                MultipleChoiceOption("A", "A. Use AWS KMS."),
                MultipleChoiceOption("B", "B. Use Amazon S3."),
            ],
            correct_option_ids=["A"],
        ),
    )

    assert correct_answer_text(question) == "AWS KMS"

def test_answer_feature_extractor_defaults_to_long_form_answer():
    question = _structured_question("manages encryption keys")
    extractor = AnswerFeatureExtractor()

    features = dict(zip(extractor.feature_names, extractor.extract(question, "AWS KMS")))

    assert features["reference_jaccard"] > 0
    assert features["short_answer_jaccard"] == 0

def test_answer_feature_extractor_can_enable_short_form_answer():
    question = _structured_question("manages encryption keys")
    extractor = AnswerFeatureExtractor(answer_form="short")

    features = dict(zip(extractor.feature_names, extractor.extract(question, "AWS KMS")))

    assert features["reference_jaccard"] == 0
    assert features["short_answer_jaccard"] > 0


def test_answer_feature_extractor_uses_official_alias_and_distractor_evidence():
    question = _structured_question("managed build project")
    extractor = AnswerFeatureExtractor(answer_form="both")

    correct_features = dict(zip(extractor.feature_names, extractor.extract(question, "AWS Code Build")))
    distractor_features = dict(zip(extractor.feature_names, extractor.extract(question, "CodeDeploy AppSpec")))

    assert correct_features["acceptable_answer_exact"] == 1.0
    assert correct_features["acceptable_answer_jaccard"] > 0
    assert distractor_features["incorrect_distinctive_token_coverage"] > correct_features["incorrect_distinctive_token_coverage"]
    assert distractor_features["common_misconception_coverage"] > 0
