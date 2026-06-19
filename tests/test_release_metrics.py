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
    evaluate_semantic_curated_answers,
    semantic_similarity_score,
)
from aws_certification_coach.questions.json_repository import JsonQuestionRepository
from aws_certification_coach.training.features import AnswerFeatureExtractor, correct_answer_text
from scripts.plot_training_history import plot_training_history
from scripts.release_metrics import render_release_metrics, update_release_notes
from scripts.semantic_similarity_evaluation import plot_semantic_accuracy
from scripts.combine_release_charts import combine_release_charts


STRUCTURED_QUESTIONS = JsonQuestionRepository(
    Path(__file__).resolve().parents[1] / "config" / "data" / "structured_answer_training_data.json"
).all()


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


def test_training_graph_writes_png_from_checkpoint_json(tmp_path: Path):
    history = tmp_path / "history.json"
    history.write_text(
        '{"checkpoints": [{"epoch": 1, "mse": 0.4, "mae": 0.5, "curated_grade_accuracy": 0.4}, '
        '{"epoch": 5, "mse": 0.2, "mae": 0.3, "curated_grade_accuracy": 0.6}]}',
        encoding="utf-8",
    )
    output = tmp_path / "training.png"
    accuracy_output = tmp_path / "accuracy.png"

    plot_training_history(history, output, accuracy_output)

    assert output.read_bytes().startswith(b"\x89PNG")
    assert accuracy_output.read_bytes().startswith(b"\x89PNG")


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


def test_semantic_accuracy_chart_includes_answer_model_within_one_letter_metric(tmp_path: Path):
    output = tmp_path / "semantic_accuracy.png"

    plot_semantic_accuracy(
        {
            "semantic_grade_accuracy": 0.8,
            "semantic_precision": 0.9,
            "semantic_recall": 0.75,
            "semantic_exact_letter_accuracy": 0.64,
        },
        output,
        {"splits": {"test": {"within_one_letter_accuracy": 0.92}}},
    )

    assert output.read_bytes().startswith(b"\x89PNG")


def test_question_coverage_metrics_and_chart_write_png(tmp_path: Path):
    rows = [
        {
            "certification": "AWS Certified Developer",
            "domain": "Development with AWS Services",
            "difficulty": "Medium",
            "question_type": "service_comparison",
            "question": "Compare Lambda with SQS for this retry scenario.",
            "key_concepts": ["Lambda", "SQS", "dead-letter queue"],
            "original_multiple_choice": {"source_name": "AWS Documentation: Lambda"},
        },
        {
            "certification": "AWS Certified Developer",
            "domain": "Development with AWS Services",
            "difficulty": "Medium",
            "question": "Which service should run code when a schedule fires?",
            "key_concepts": ["Lambda", "EventBridge"],
            "original_multiple_choice": {"source_name": "AWS Documentation: EventBridge"},
        },
        {
            "certification": "Solutions Architect Associate",
            "domain": "Storage",
            "difficulty": "Easy",
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
    assert {"name": "Comparison tradeoff", "count": 1} in metrics["question_intents"]
    assert {"name": "Service or feature selection", "count": 1} in metrics["question_intents"]
    assert {"name": "Configuration decision", "count": 1} in metrics["question_intents"]
    assert set(outputs) == {"domain", "intent", "certification"}
    for output in outputs.values():
        assert output.read_bytes().startswith(b"\x89PNG")
        width, height = _png_dimensions(output)
        assert width >= 1500
        assert height >= 1000


def test_question_coverage_shell_wrapper_accepts_release_tag(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[1]
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


def test_combine_release_charts_writes_four_panel_png(tmp_path: Path):
    chart_paths = []
    for index, title in enumerate(["Semantic", "Domain", "Intent", "Certification"]):
        path = tmp_path / f"chart_{index}.png"
        _write_sample_chart(path, title)
        chart_paths.append((title, path))
    output = tmp_path / "release_metrics_chart.png"

    combine_release_charts(chart_paths, output)

    assert output.read_bytes().startswith(b"\x89PNG")
    width, height = _png_dimensions(output)
    assert width >= 2500
    assert height >= 1800


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


def test_release_metrics_tracks_curated_and_semantic_accuracy(tmp_path: Path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "training_history.json").write_text(
        '{"checkpoints": [{"epoch": 1, "mse": 0.1234, "mae": 0.5678, "curated_grade_accuracy": 0.44}]}',
        encoding="utf-8",
    )
    (metrics_dir / "training_metrics.json").write_text(
        '{"answer_form": "long", "saved_model": {"curated_grade_accuracy": 0.96, "calibration_count": 18}}',
        encoding="utf-8",
    )
    (metrics_dir / "semantic_similarity.json").write_text(
        '{"semantic_grade_accuracy": 0.8, "semantic_precision": 0.9, "semantic_recall": 0.75, '
        '"semantic_exact_letter_accuracy": 0.64, "semantic_example_count": 25}',
        encoding="utf-8",
    )
    (metrics_dir / "answer_model_evaluation.json").write_text(
        (
            '{"splits": {'
            '"train": {"within_one_letter_accuracy": 0.91}, '
            '"validation": {"within_one_letter_accuracy": 0.82}, '
            '"test": {"within_one_letter_accuracy": 0.76}'
            "}}"
        ),
        encoding="utf-8",
    )
    (metrics_dir / "answer_model_evaluation.md").write_text(
        (
            "| Split | Examples | Within 1 Letter | Exact Letter | MAE | MSE |\n"
            "|---|---:|---:|---:|---:|---:|\n"
            "| Test | 25 | 76.0% | 64.0% | 0.1200 | 0.0300 |\n"
        ),
        encoding="utf-8",
    )
    (metrics_dir / "question_fidelity.json").write_text(
        '{"model_name": "question_fidelity_heuristic_v1", "question_fidelity": 88.4, "sample_count": 5, "source_count": 12, "generated_question_count": 12}',
        encoding="utf-8",
    )
    (metrics_dir / "question_coverage.json").write_text(
        (
            '{"question_count": 92, "domain_count": 15, "concept_count": 184, "question_intent_count": 4, '
            '"covered_services": [{"name": "Lambda", "count": 3}, {"name": "SQS", "count": 2}], '
            '"top_concepts": [{"name": "serverless", "count": 4}, {"name": "replication", "count": 3}]}'
        ),
        encoding="utf-8",
    )

    markdown = render_release_metrics(metrics_dir, release_label="v1.5 Schema")

    assert (
        "| Release | Semantic Accuracy | Semantic Precision | Semantic Recall | "
        "Exact Letter Accuracy | Within 1 Letter | Question Fidelity |"
    ) in markdown
    assert "| v1.5 Schema | 80.00% | 90.00% | 75.00% | 64.00% | 76.00% | 88.40% |" in markdown
    assert "## Answer Model Split Evaluation" in markdown
    assert "| Test | 25 | 76.0% | 64.0% | 0.1200 | 0.0300 |" in markdown
    assert "Saved model grade-band accuracy" not in markdown
    assert "Training accuracy" not in markdown

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

def test_semantic_similarity_uses_syntax_alias_table_for_service_names():
    cloudtrail_question = _structured_question("records AWS API activity")
    codebuild_question = _structured_question("managed build project")

    assert semantic_similarity_score(cloudtrail_question, "AWS Cloud trail records API activity for auditing.") >= 90
    assert semantic_similarity_score(cloudtrail_question, "Use AWS CloudTrail.") >= 90
    assert semantic_similarity_score(codebuild_question, "AWS Code Build") >= 80

def test_semantic_similarity_uses_acceptable_answers_as_correct_evidence():
    question = _structured_question("managed build project")

    assert semantic_similarity_score(question, "AWS Code Build") >= 90

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
    assert metrics["semantic_matching_letter_grades"] == 0
    assert metrics["semantic_mismatches"][0]["expected_letter"] == "A"
    assert metrics["semantic_mismatches"][0]["actual_letter"] == "B"

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

    assert semantic_similarity_score(secrets_question, "AWS KMS Keys") < 60
    assert semantic_similarity_score(s3_question, "S3 version tracking") < 60

def test_semantic_similarity_caps_question_rephrases_without_answer_detail():
    question = _structured_question("custom token validation")

    assert semantic_similarity_score(
        question,
        "Which API Gateway feature should be used to run token validation on requests?",
    ) < 80
    assert semantic_similarity_score(question, "Use an API Gateway Lambda authorizer.") >= 80

def test_correct_answer_text_uses_multiple_choice_value_without_answer_cue():
    question = Question(
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
