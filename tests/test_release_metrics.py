from pathlib import Path

from aws_certification_coach.release_metrics.complexity import measure_complexity
from scripts.plot_training_history import plot_training_history


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
