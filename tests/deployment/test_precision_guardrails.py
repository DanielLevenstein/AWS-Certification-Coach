from pathlib import Path

import pytest

from scripts.check_precision_guardrails import check_release_guardrails


def test_release_guardrails_pass_when_release_metrics_and_grade_tables_are_present(tmp_path: Path):
    release_notes = _release_notes(
        tmp_path,
        release_label="v9.9.9",
        semantic_accuracy="1.00%",
        semantic_precision="2.00%",
        question_fidelity="3.00%",
    )

    check_release_guardrails(release_notes, "v9.9.9")


def test_release_guardrails_require_release_in_grade_precision_tables(tmp_path: Path):
    release_notes = _release_notes(tmp_path, release_label="v9.9.9", include_grade_precision=False)

    with pytest.raises(SystemExit, match="Grade Precision table"):
        check_release_guardrails(release_notes, "v9.9.9")


def test_release_guardrails_require_release_as_last_precision_table_row(tmp_path: Path):
    release_notes = _release_notes(tmp_path, release_label="v9.9.9", newer_release_label="v9.9.10")

    with pytest.raises(SystemExit, match="Grade Band Precision last row is not v9.9.9"):
        check_release_guardrails(release_notes, "v9.9.9")


def test_release_guardrails_require_release_in_generated_metrics(tmp_path: Path):
    release_notes = _release_notes(tmp_path, release_label="v9.9.9", include_generated_metrics=False)

    with pytest.raises(SystemExit, match="Generated Release Metrics table"):
        check_release_guardrails(release_notes, "v9.9.9")


def test_deploy_script_runs_release_guardrail_hook_before_build():
    deploy_script = Path("deploy.sh").read_text(encoding="utf-8")

    guardrail_index = deploy_script.index("scripts/check_precision_guardrails.py")
    build_index = deploy_script.index("docker buildx build")
    assert guardrail_index < build_index
    assert '--release-label "$TAG_ID"' in deploy_script


def _release_notes(
    tmp_path: Path,
    *,
    release_label: str,
    include_grade_band: bool = True,
    include_grade_precision: bool = True,
    include_generated_metrics: bool = True,
    newer_release_label: str = "",
    semantic_accuracy: str = "98.00%",
    semantic_precision: str = "99.00%",
    question_fidelity: str = "95.12%",
) -> Path:
    grade_band_row = f"| {release_label} | 100.00% | 96.00% | 97.00% |" if include_grade_band else ""
    newer_grade_band_row = (
        f"\n| {newer_release_label} | 100.00% | 96.00% | 97.00% |" if newer_release_label else ""
    )
    grade_precision_row = (
        f"| {release_label} | 100.00% | 95.00% | 91.00% | 96.00% | 94.00% |"
        if include_grade_precision
        else ""
    )
    newer_grade_precision_row = (
        f"\n| {newer_release_label} | 100.00% | 95.00% | 91.00% | 96.00% | 94.00% |"
        if newer_release_label
        else ""
    )
    generated_metrics_row = (
        f"| {release_label} | {semantic_accuracy} | {semantic_precision} | 98.00% | "
        f"97.00% | 99.00% | {question_fidelity} |"
        if include_generated_metrics
        else ""
    )
    path = tmp_path / "RELEASE_NOTES.md"
    path.write_text(
        f"""# Release Notes

### Grade Band Precision
| Release | A | B&C | D&F |
|:--------|--:|----:|----:|
{grade_band_row}{newer_grade_band_row}

## Grade Precision
| Release | A | B | C | D | F |
|:--------|--:|--:|--:|--:|--:|
{grade_precision_row}{newer_grade_precision_row}

<!-- release-metrics:start -->
## Generated Release Metrics

| Release | Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Within 1 Letter | Question Fidelity |
|:--------|------------------:|-------------------:|----------------:|----------------------:|----------------:|------------------:|
{generated_metrics_row}
<!-- release-metrics:end -->
""",
        encoding="utf-8",
    )
    return path
