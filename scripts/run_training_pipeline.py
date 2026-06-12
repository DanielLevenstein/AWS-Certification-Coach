#!/usr/bin/env python3
"""
Helper script to run the complete model training pipeline.

This orchestrates:
1. Data generation (questions and artifacts)
2. Question transformation (MCQ -> freeform)
3. Answer classifier training
4. Partial-credit regressor training

Usage:
    python scripts/run_training_pipeline.py                    # Run all steps
    python scripts/run_training_pipeline.py --skip-generation  # Skip data generation
    python scripts/run_training_pipeline.py --classifier-only  # Only train classifier
    python scripts/run_training_pipeline.py --regressor-only   # Only train regressor
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class TrainingPipeline:
    """Orchestrates model training pipeline."""

    def __init__(
        self,
        skip_generation: bool = False,
        skip_transform: bool = False,
        classifier_only: bool = False,
        regressor_only: bool = False,
        eval_mode: str = "leave-one-question-out",
        verbose: bool = False,
    ):
        self.skip_generation = skip_generation
        self.skip_transform = skip_transform
        self.classifier_only = classifier_only
        self.regressor_only = regressor_only
        self.eval_mode = eval_mode
        self.verbose = verbose
        self.workspace_root = self._find_workspace_root()

    def _find_workspace_root(self) -> Path:
        """Find the workspace root directory."""
        current = Path(__file__).parent.parent
        if (current / "pyproject.toml").exists():
            return current
        raise RuntimeError("Could not find workspace root")

    def _copy_config_data(self) -> None:
        """Copy curated training data from config/ to data/curated/."""
        curated_dir = self.workspace_root / "data" / "curated"
        curated_dir.mkdir(parents=True, exist_ok=True)

        files_to_copy = [
            ("config/curated_training_data.json", "data/curated/curated_training_data.json"),
            ("config/user_feedback.v1.json", "data/curated/user_feedback.v1.json"),
        ]

        for src_rel, dst_rel in files_to_copy:
            src_path = self.workspace_root / src_rel
            dst_path = self.workspace_root / dst_rel

            if src_path.exists():
                if self.verbose:
                    print(f"Copying {src_rel} → {dst_rel}")
                shutil.copy2(src_path, dst_path)
            else:
                if self.verbose:
                    print(f"⚠ Source file not found: {src_rel}")

    def run(self) -> int:
        """Run the complete training pipeline."""
        try:
            print("=" * 70)
            print("AWS Certification Coach - Model Training Pipeline")
            print("=" * 70)
            print()

            # Always copy config data to curated directory first
            self._copy_config_data()

            if not self.regressor_only and not self.classifier_only:
                if not self.skip_generation:
                    self._run_step("Data Generation", self._run_data_generation)
                if not self.skip_transform:
                    self._run_step("Question Transformation", self._run_transformation)

            if not self.regressor_only:
                self._run_step("Answer Classifier Training", self._run_classifier_training)

            if not self.classifier_only:
                self._run_step("Partial-Credit Regressor Training", self._run_regressor_training)

            print()
            print("=" * 70)
            print("✓ Training pipeline completed successfully")
            print("=" * 70)
            return 0

        except subprocess.CalledProcessError as e:
            print()
            print("=" * 70)
            print(f"✗ Training pipeline failed at step with exit code {e.returncode}")
            print("=" * 70)
            return 1
        except Exception as e:
            print()
            print("=" * 70)
            print(f"✗ Unexpected error: {e}")
            print("=" * 70)
            return 1

    def _run_step(self, step_name: str, step_func) -> None:
        """Run a single pipeline step with timing."""
        print(f"\n[Step] {step_name}")
        print("-" * 70)
        start_time = time.time()

        try:
            step_func()
            elapsed = time.time() - start_time
            print(f"✓ {step_name} completed in {elapsed:.1f}s")
        except subprocess.CalledProcessError as e:
            elapsed = time.time() - start_time
            print(f"✗ {step_name} failed after {elapsed:.1f}s")
            raise

    def _run_data_generation(self) -> None:
        """Run data generation scripts."""
        self._run_command(
            ["python", "scripts/generate_sample_training_artifacts.py"],
            "Generating sample training artifacts...",
        )
        self._run_command(
            ["python", "scripts/generate_app_question_artifacts.py", "--count", "80"],
            "Generating app-facing question artifacts...",
        )

    def _run_transformation(self) -> None:
        """Run question transformation (MCQ -> freeform)."""
        input_file = self.workspace_root / "data" / "questions" / "sample_questions.json"
        output_file = self.workspace_root / "data" / "generated" / "questions_transformed.json"

        if not input_file.exists():
            print(f"⚠ Skipping transformation: input file not found ({input_file})")
            return

        self._run_command(
            [
                "python",
                "scripts/transform_questions.py",
                "--input",
                str(input_file),
                "--output",
                str(output_file),
                "--provider",
                "heuristic",  # Use heuristic by default to avoid API calls
            ],
            "Transforming questions to freeform format...",
        )

    def _run_classifier_training(self) -> None:
        """Run answer classifier training."""
        cmd = [
            "python",
            "scripts/train_answer_classifier.py",
            "--eval-mode",
            self.eval_mode,
        ]
        self._run_command(cmd, "Training answer classifier...")

    def _run_regressor_training(self) -> None:
        """Run partial-credit regressor training."""
        cmd = [
            "python",
            "scripts/train_partial_answer_regressor.py",
            "--eval-mode",
            self.eval_mode,
        ]
        self._run_command(cmd, "Training partial-credit regressor...")

    def _run_command(self, cmd: list[str], description: str) -> None:
        """Run a shell command."""
        if self.verbose:
            print(description)
            print(f"  Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=self.workspace_root,
            capture_output=not self.verbose,
            text=True,
        )

        if result.returncode != 0:
            if not self.verbose:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
            raise subprocess.CalledProcessError(result.returncode, cmd)

        if not self.verbose and result.stdout:
            # Show summary output even in non-verbose mode
            lines = result.stdout.strip().split("\n")
            if lines:
                print(f"  → {lines[-1]}")


def main() -> int:
    """Parse arguments and run training pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the complete model training pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_training_pipeline.py
    Run complete pipeline (data generation → transformation → training)

  python scripts/run_training_pipeline.py --skip-generation
    Skip data generation, run transformation and training

  python scripts/run_training_pipeline.py --classifier-only
    Train only the answer classifier

  python scripts/run_training_pipeline.py --regressor-only
    Train only the partial-credit regressor

  python scripts/run_training_pipeline.py --verbose
    Run with detailed output for debugging
        """,
    )

    parser.add_argument(
        "--skip-generation",
        action="store_true",
        help="Skip data generation step",
    )
    parser.add_argument(
        "--skip-transform",
        action="store_true",
        help="Skip question transformation step",
    )
    parser.add_argument(
        "--classifier-only",
        action="store_true",
        help="Train only the answer classifier",
    )
    parser.add_argument(
        "--regressor-only",
        action="store_true",
        help="Train only the partial-credit regressor",
    )
    parser.add_argument(
        "--eval-mode",
        choices=["leave-one-question-out", "training"],
        default="leave-one-question-out",
        help="Evaluation mode for model training (default: leave-one-question-out)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    # Validate mutually exclusive options
    if args.classifier_only and args.regressor_only:
        parser.error("Cannot specify both --classifier-only and --regressor-only")

    pipeline = TrainingPipeline(
        skip_generation=args.skip_generation,
        skip_transform=args.skip_transform,
        classifier_only=args.classifier_only,
        regressor_only=args.regressor_only,
        eval_mode=args.eval_mode,
        verbose=args.verbose,
    )

    return pipeline.run()


if __name__ == "__main__":
    sys.exit(main())
