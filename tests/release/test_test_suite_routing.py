"""Contract tests for the independent test-suite command boundaries."""

from pathlib import Path

import pytest

import test_suites


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_unit_suite_excludes_model_smoke_and_deployment(monkeypatch):
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)

    test_suites.run_unit_tests()

    command = commands[0]
    assert "--ignore=tests/deployment" in command
    assert "--ignore=tests/model_smoke" in command


def test_model_smoke_suite_is_read_only_and_does_not_train(monkeypatch):
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)
    monkeypatch.setattr(test_suites, "_artifact_snapshot", lambda: {"models/model.json": (10, 20)})

    test_suites.run_model_smoke_tests()

    assert commands[0][-1] == "tests/model_smoke"
    assert "model_evaluation.py" not in commands[0]


def test_model_smoke_suite_rejects_artifact_writes(monkeypatch):
    snapshots = iter(({}, {"metrics/unexpected.json": (10, 20)}))
    monkeypatch.setattr(test_suites, "_run", lambda _command: None)
    monkeypatch.setattr(test_suites, "_artifact_snapshot", lambda: next(snapshots))

    with pytest.raises(RuntimeError, match="modified generated/model artifacts"):
        test_suites.run_model_smoke_tests()


def test_deployment_has_an_explicit_route(monkeypatch):
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)

    test_suites.run_deployment_tests()

    assert "tests/deployment" in commands[0]


def test_full_release_runs_fast_checks_without_duplicate_model_training():
    release_script = (PROJECT_ROOT / "release_notes.sh").read_text(encoding="utf-8")

    assert "test_suites.py unit" in release_script
    assert "test_suites.py model-smoke" in release_script
    assert "test_suites.py model-training" not in release_script
    assert 'RELEASE_SUITE="release-quick"' in release_script


def test_quick_release_reuses_complete_metrics_without_training(tmp_path, monkeypatch):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    for name in test_suites.QUICK_RELEASE_ARTIFACTS:
        path = metrics_dir / name
        path.write_text("{}", encoding="utf-8")
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)

    test_suites.run_quick_release_metrics(
        ["--metrics-dir", str(metrics_dir), "--release-label", "v2.quick"]
    )

    assert len(commands) == 1
    assert "scripts/release_metrics.py" in commands[0]
    assert "scripts/semantic_similarity_evaluation.py" not in commands[0]


def test_summary_only_release_skips_precision_gated_chart_outputs(tmp_path, monkeypatch):
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)

    test_suites.run_release_metrics(
        ["--metrics-dir", str(tmp_path / "metrics"), "--release-label", "diagnostic", "--summary-only"]
    )

    semantic_commands = [command for command in commands if "scripts/semantic_similarity_evaluation.py" in command]
    assert len(semantic_commands) == 1
    assert "--per-grade-output" not in semantic_commands[0]
    assert "--grade-band-output" not in semantic_commands[0]
    assert any("scripts/release_metrics.py" in command for command in commands)


def test_summary_only_quick_release_requires_only_semantic_metrics(tmp_path, monkeypatch):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    (metrics_dir / "semantic_similarity.json").write_text("{}", encoding="utf-8")
    commands = []
    monkeypatch.setattr(test_suites, "_run", commands.append)

    test_suites.run_quick_release_metrics(
        ["--metrics-dir", str(metrics_dir), "--release-label", "diagnostic", "--summary-only"]
    )

    assert len(commands) == 1
    assert "scripts/release_metrics.py" in commands[0]


def test_quick_release_rejects_incomplete_metrics(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing artifacts"):
        test_suites.run_quick_release_metrics(["--metrics-dir", str(tmp_path)])


def test_all_test_modules_are_grouped_by_review_area():
    assert list((PROJECT_ROOT / "tests").glob("test_*.py")) == []


def test_suite_parser_no_longer_exposes_model_training():
    help_text = test_suites._suite_parser().format_help()

    assert "model-training" not in help_text
