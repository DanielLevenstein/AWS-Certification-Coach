from pathlib import Path

from aws_certification_coach.release_metrics.complexity import measure_complexity
from aws_certification_coach.domain import MultipleChoiceOption, MultipleChoiceQuestion, Question
from aws_certification_coach.model_evaluation.semantic_similarity import semantic_similarity_score
from scripts.plot_training_history import plot_training_history
from scripts.release_metrics import render_release_metrics


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


def test_release_metrics_tracks_curated_and_semantic_accuracy(tmp_path: Path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "training_history.json").write_text(
        '{"checkpoints": [{"epoch": 1, "mse": 0.1234, "mae": 0.5678, "curated_grade_accuracy": 0.44}]}',
        encoding="utf-8",
    )
    (metrics_dir / "semantic_similarity.json").write_text(
        '{"semantic_grade_accuracy": 0.8}',
        encoding="utf-8",
    )

    markdown = render_release_metrics(metrics_dir)

    assert "| Curated grade-band accuracy | Semantic-aware grading |" in markdown
    assert "| 44.00% | 80.00% |" in markdown
    assert "Generated-label regression metrics are still written for diagnostics" in markdown


def test_semantic_similarity_recognizes_aliases_and_concepts():
    question = Question(
        question_id="Q1",
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
