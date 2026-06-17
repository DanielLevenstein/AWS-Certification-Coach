---
name: train-local-semantic-models
description: Train, evaluate, and release-gate local semantic models for AWS Certification Coach. Use when adding a separate question-fidelity, semantic-grading, or heuristic semantic model; when creating model-training scripts; when checking train/validation/test separation; when updating release metrics for local model quality; or when ensuring model weights and artifacts remain independent.
---

# Train Local Semantic Models

## Overview

Use this skill to add or update local semantic models in AWS Certification Coach without mixing app data, training labels, final verification data, or unrelated model weights. Prefer deterministic, inspectable Python models and release metrics over opaque runtime dependencies.

## Workflow

1. Read the task-specific design doc or `docs/TODO.md`.
2. Identify the target model family and confirm whether it scores answers, question fidelity, or another dimension.
3. Read `references/data-contracts.md` before touching data loaders or generated artifacts.
4. Read `references/release-workflow.md` before adding release metrics, gates, or commit-ready changes.
5. Implement model contracts, feature extraction, training, evaluation, and tests as separate modules.
6. Run validation scripts in the project virtual environment.
7. Confirm generated `/data/`, `/scripts/data/`, and `/metrics/` artifacts are not staged.

## Model Boundaries

- Keep question-fidelity models separate from answer semantic-evaluation models.
- Do not reuse answer model weights, thresholds, calibration rows, metrics files, or release gates for question fidelity.
- Reuse generic helpers only when they are model-neutral, such as tokenization, score clamping, or JSON writing.
- Store a new source under a clearly named package such as `src/aws_certification_coach/question_fidelity/` or a similarly specific module.
- Name scripts by the model they train or evaluate, for example `scripts/train_question_fidelity.py`.

## Training Standards

- Run Python through `.venv/bin/python`; create the virtual environment first if needed.
- Keep train, validation, and final test splits explicit in script arguments.
- Fail training when too few examples are available to make the metric meaningful.
- Persist model artifacts only when the validation gate passes, unless the task explicitly asks for diagnostic artifacts.
- Write metrics as JSON with stable keys so `scripts/release_metrics.py` can render them.
- Add tests that prove verification/test data is not used as training data.

## Question Fidelity Pattern

For question expansion to work, the model should compare a source concept bundle with a generated freeform question and reference answer. It should return a 0-100 score plus covered, missing, and conflicting concepts. It should not judge learner answers.

Use a dedicated artifact such as `models/question_fidelity_model.json` and metrics such as `models/question_fidelity_model_metrics.json` or a release metrics JSON under the configured metrics directory.

## Validation Commands

Use the existing project scripts unless the task requires a narrower check:

```bash
./clean.sh
./setup.sh
./run_unit_tests.sh
./run_model_tests.sh
./release_notes_full.sh <release-tag>
```

Do not run or start the Streamlit app unless the user asks.

## References

- Read `references/data-contracts.md` before changing data schemas, source question ingestion, generated artifacts, or tests around split integrity.
- Read `references/release-workflow.md` before changing release metrics, release notes, model gates, or commit preparation.
