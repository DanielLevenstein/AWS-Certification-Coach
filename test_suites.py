#!/usr/bin/env python3
"""Root-level helpers for independent unit, model, release, and deployment suites."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
QUICK_RELEASE_ARTIFACTS = (
    "semantic_similarity.json",
    "question_fidelity.json",
    "question_coverage.json",
    "knowledge_base.json",
    "semantic_accuracy.png",
    "per_grade_metrics.png",
    "grade_band_metrics.png",
    "grade_distribution_metrics.png",
    "question_domain_coverage.png",
    "question_intent_coverage.png",
    "question_certification_coverage.png",
    "curated_failure_report.md",
    "curated_rubric_review.md",
)
QUICK_RELEASE_SUMMARY_ARTIFACTS = (
    "semantic_similarity.json",
)


def run_unit_tests(extra_args: list[str] | None = None) -> None:
    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "--ignore=tests/deployment",
            "--ignore=tests/model_smoke",
            *(extra_args or []),
        ]
    )


def run_model_smoke_tests(extra_args: list[str] | None = None) -> None:
    before = _artifact_snapshot()
    _run([sys.executable, "-m", "pytest", "tests/model_smoke", *(extra_args or [])])
    after = _artifact_snapshot()
    if after != before:
        changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
        raise RuntimeError(f"Model smoke tests modified generated/model artifacts: {changed}")


def run_deployment_tests(extra_args: list[str] | None = None) -> None:
    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/deployment",
            *(extra_args or []),
        ]
    )


def run_release_metrics(extra_args: list[str] | None = None) -> None:
    args = _parse_release_args(extra_args)
    metrics_dir = args.metrics_dir or timestamped_metrics_dir()
    _run(
        [
            sys.executable,
            "scripts/curated_failure_report.py",
            "--output",
            str(metrics_dir / "curated_failure_report.md"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/curated_rubric_review.py",
            "--output",
            str(metrics_dir / "curated_rubric_review.md"),
        ]
    )
    semantic_command = [
        sys.executable,
        "scripts/semantic_similarity_evaluation.py",
        "--output",
        str(metrics_dir / "semantic_similarity.json"),
        "--chart-output",
        str(metrics_dir / "semantic_accuracy.png"),
    ]
    if not args.summary_only:
        semantic_command.extend(
            [
                "--per-grade-output",
                str(metrics_dir / "per_grade_metrics.png"),
                "--grade-band-output",
                str(metrics_dir / "grade_band_metrics.png"),
                "--grade-distribution-output",
                str(metrics_dir / "grade_distribution_metrics.png"),
            ]
        )
    _run(semantic_command)
    _run(
        [
            sys.executable,
            "scripts/question_fidelity_evaluation.py",
            "--output",
            str(metrics_dir / "question_fidelity.json"),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/generate_question_coverage.py",
            "--output",
            str(metrics_dir / "question_coverage.json"),
            "--chart-output-dir",
            str(metrics_dir),
        ]
    )
    _run(
        [
            sys.executable,
            "scripts/knowledge_base_metrics.py",
            "--output",
            str(metrics_dir / "knowledge_base.json"),
        ]
    )
    _run([sys.executable, "scripts/quality_metrics.py", "--output-dir", str(metrics_dir)])
    _render_release_summary(args, metrics_dir)
    print(f"Release metrics directory: {metrics_dir}")


def run_quick_release_metrics(extra_args: list[str] | None = None) -> None:
    """Refresh release-note Markdown from an existing full metrics run."""

    args = _parse_release_args(extra_args)
    if args.metrics_dir is None:
        raise ValueError("Quick release metrics require --metrics-dir from a previous full run.")
    required_artifacts = QUICK_RELEASE_SUMMARY_ARTIFACTS if args.summary_only else QUICK_RELEASE_ARTIFACTS
    missing = [name for name in required_artifacts if not (args.metrics_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Quick release metrics are missing artifacts: {missing}")
    _render_release_summary(args, args.metrics_dir)
    print(f"Reused release metrics directory without training: {args.metrics_dir}")


def _parse_release_args(extra_args: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-label", default="Current")
    parser.add_argument("--release-notes", default=None)
    parser.add_argument("--metrics-dir", type=Path, default=None)
    parser.add_argument("--strict-grading", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args(extra_args or [])


def _render_release_summary(args: argparse.Namespace, metrics_dir: Path) -> None:
    release_metrics_command = [
        sys.executable,
        "scripts/release_metrics.py",
        "--metrics-dir",
        str(metrics_dir),
        "--output",
        str(metrics_dir / "summary.md"),
        "--release-label",
        args.release_label,
    ]
    if args.release_notes is not None:
        release_metrics_command.extend(["--release-notes", args.release_notes])
    if args.strict_grading:
        release_metrics_command.append("--strict-grading")
    _run(release_metrics_command)


def timestamped_metrics_dir() -> Path:
    return Path("metrics") / datetime.now().strftime("%Y%m%d_%H%M%S")


def _artifact_snapshot() -> dict[str, tuple[int, int]]:
    snapshot = {}
    for directory_name in ("models", "data", "metrics"):
        directory = ROOT / directory_name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                stat = path.stat()
                snapshot[str(path.relative_to(ROOT))] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def main() -> None:
    help_parser = _suite_parser()
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        help_parser.print_help()
        return
    parser = _suite_parser(add_help=False)
    args, extra_args = parser.parse_known_args()
    {
        "unit": run_unit_tests,
        "model-smoke": run_model_smoke_tests,
        "release": run_release_metrics,
        "release-quick": run_quick_release_metrics,
        "deployment": run_deployment_tests,
    }[args.suite](extra_args)


def _suite_parser(add_help: bool = True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument(
        "suite",
        choices=["unit", "model-smoke", "release", "release-quick", "deployment"],
    )
    return parser


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
