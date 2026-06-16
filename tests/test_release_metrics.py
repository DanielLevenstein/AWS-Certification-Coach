from pathlib import Path

from aws_certification_coach.release_metrics.complexity import measure_complexity
from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from aws_certification_coach.training.features import AnswerFeatureExtractor, correct_answer_text
from scripts.plot_training_history import plot_training_history
from scripts.release_metrics import render_release_metrics, update_release_notes
from scripts.semantic_similarity_evaluation import _saved_model_accuracy, plot_semantic_accuracy


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
        },
        output,
    )

    assert output.read_bytes().startswith(b"\x89PNG")


def test_semantic_accuracy_chart_accepts_saved_model_accuracy(tmp_path: Path):
    output = tmp_path / "semantic_accuracy.png"

    plot_semantic_accuracy(
        {
            "semantic_grade_accuracy": 0.8,
            "semantic_precision": 0.9,
            "semantic_recall": 0.75,
        },
        output,
        saved_model_accuracy=0.96,
    )

    assert output.read_bytes().startswith(b"\x89PNG")


def test_saved_model_accuracy_reads_training_metrics(tmp_path: Path):
    training_metrics = tmp_path / "training_metrics.json"
    training_metrics.write_text(
        '{"saved_model": {"curated_grade_accuracy": 0.96}}',
        encoding="utf-8",
    )

    assert _saved_model_accuracy(training_metrics) == 0.96


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
        '{"semantic_grade_accuracy": 0.8, "semantic_precision": 0.9, "semantic_recall": 0.75}',
        encoding="utf-8",
    )

    markdown = render_release_metrics(metrics_dir, release_label="v1.5 Schema")

    assert "| Release | Saved Model Accuracy | Training Accuracy | Semantic Accuracy | Semantic Precision | Semantic Recall |" in markdown
    assert "| v1.5 Schema | 96.00% | 44.00% | 80.00% | 90.00% | 75.00% |" in markdown
    assert "Saved model answer form: `long`" in markdown
    assert "Saved model calibration count: `18`" in markdown
    assert "Semantic precision is the release guardrail" in markdown
    assert "`semantic_similarity` diagnostic chart: `semantic_accuracy.png`" in markdown
    assert "A/B and C/D as accepted answers and F as rejected" in markdown


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
    question = Question(
        certification="Cloud Practitioner",
        domain="Security",
        difficulty="Easy",
        question="Which service manages encryption keys?",
        reference_answer="Use AWS KMS to create and manage encryption keys.",
        key_concepts=["AWS KMS", "encryption keys", "key management"],
        original_multiple_choice=MultipleChoiceQuestion(
            question="Which service manages encryption keys?",
            options=[
                MultipleChoiceOption("A", "Use AWS KMS."),
                MultipleChoiceOption("B", "Use Amazon S3."),
            ],
            correct_option_ids=["A"],
        ),
    )

    assert semantic_similarity_score(question, "KMS manages encryption keys.") >= 80
    assert semantic_similarity_score(question, "Use Amazon S3.") < 60


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
                MultipleChoiceOption("A", "Use AWS KMS."),
                MultipleChoiceOption("B", "Use Amazon S3."),
            ],
            correct_option_ids=["A"],
        ),
    )
    extractor = AnswerFeatureExtractor()

    features = dict(zip(extractor.feature_names, extractor.extract(question, "AWS KMS")))

    assert features["reference_jaccard"] > 0
    assert features["short_answer_jaccard"] == 0


def test_answer_feature_extractor_can_enable_short_form_answer():
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
                MultipleChoiceOption("A", "Use AWS KMS."),
                MultipleChoiceOption("B", "Use Amazon S3."),
            ],
            correct_option_ids=["A"],
        ),
    )
    extractor = AnswerFeatureExtractor(answer_form="short")

    features = dict(zip(extractor.feature_names, extractor.extract(question, "AWS KMS")))

    assert features["reference_jaccard"] == 0
    assert features["short_answer_jaccard"] > 0
