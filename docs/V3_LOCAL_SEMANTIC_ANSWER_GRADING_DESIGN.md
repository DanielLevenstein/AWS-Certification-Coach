# v3.0.0 Local Semantic Answer Grading Design

Status: Proposed  
Target release: `v3.0.0`  
Scope: Learner-answer grading only  
Related documents: `docs/ANSWER_RUBRIC.md`, `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_ARCHITECTURE.md`, `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_METRICS.md`

## Decision Summary

Version 3 replaces production lexical and hand-calibrated answer scoring with a fully local, two-layer grading system:

1. A pinned SentenceTransformer encoder converts learner answers and rubric evidence into normalized semantic vectors.
2. A small supervised classifier maps semantic relationship features to the shared `A`, `B`, `C`, `D`, and `F` grade scale.

The encoder is `sentence-transformers/all-MiniLM-L6-v2`. The production application does not require an OpenAI API key or another hosted inference service. Development may use an available accelerator automatically; the production Docker image runs inference in CPU-only mode.

Question-fidelity scoring remains an independent release concern. It must not share learner-answer classifier weights, datasets, thresholds, or metrics.

## Problem Statement

The version 2 scoring path evolved through binary lexical classification, partial-credit regression, deterministic semantic rules, and exact question-and-answer calibrations. Those iterations produced useful diagnostics, but they also created several problems:

- Correct paraphrases could lose credit because they did not share enough literal text with the reference answer.
- Exact calibration records could hide weaknesses in the general scorer.
- Training, production scoring, and release metrics did not always exercise the same implementation.
- Regression error did not align cleanly with exact A/B/C/D/F grading boundaries.
- Generated or curated examples could be evaluated against the same records used to tune scoring.
- Multiple legacy metrics made it difficult to determine whether a model generalized to unseen questions.

Version 3 returns to a simple supervised model, but replaces lexical normalization with semantic normalization and makes split integrity a release contract.

## Goals

- Grade semantically equivalent answers consistently even when wording differs.
- Preserve the A/B/C/D/F meanings defined in `docs/ANSWER_RUBRIC.md`.
- Run learner-answer grading locally without a hosted inference dependency.
- Keep the learned grading head small, inspectable, reproducible, and fast on CPU.
- Train on generated training examples plus explicitly approved structured examples.
- Use validation data only for model selection and release-threshold decisions.
- Use the final test split only for final reporting.
- Report exact-letter accuracy as the primary learner-answer quality metric.
- Fail model preparation when required artifacts or quality gates are missing.
- Package all inference artifacts into the production image before deployment.

## Non-Goals

- Fine-tuning the SentenceTransformer encoder in v3.0.0.
- Using learner feedback as an automatic production override.
- Loading exact question-and-answer calibrations during runtime grading.
- Training on final verification or test rows.
- Replacing question-fidelity scoring with the learner-answer classifier.
- Calling OpenAI, Hugging Face, or another external inference API at runtime.
- Generating questions during the learner study session.
- Claiming that semantic similarity alone is equivalent to rubric grading.

## Learner Experience

The learner continues to:

1. Read an AWS certification question.
2. Enter a freeform answer.
3. Receive an A/B/C/D/F grade.
4. Review missing concepts, improvement guidance, and a reference answer.

The model change should improve paraphrase handling without changing the basic quiz interaction. A concise answer may earn an A when the prompt only requires identification and the answer unambiguously identifies the correct service or feature. A prompt that explicitly asks for reasoning, constraints, multiple selections, or tradeoffs still requires that evidence for full credit.

## Grading Contract

The classifier predicts one of five ordered labels:

| Grade | Runtime score | Meaning |
|:------|--------------:|:--------|
| A | 95 | Correct and complete for the requested scope. |
| B | 85 | Mostly correct but missing one meaningful detail or constraint. |
| C | 75 | Partially correct or a plausible adjacent solution. |
| D | 65 | Minimal relevant understanding that fails the main requirement. |
| F | 25 | Incorrect, contradictory, severely misleading, or meaningless. |

The numeric score is a stable display and aggregation value. The learned target is the letter grade, not a continuous score.

## Model Design

### Semantic Encoder

The encoder is `sentence-transformers/all-MiniLM-L6-v2`.

Required release metadata:

- Hugging Face repository ID.
- Pinned repository revision or commit hash.
- Model license.
- Expected embedding dimension.
- Downloaded file manifest and checksums.
- SentenceTransformers and Transformers package versions.

The encoder produces normalized embeddings. Encoder weights are not modified during v3.0.0 classifier training.

### Semantic Relationship Features

The classifier must not learn directly from raw answer strings. For each learner answer it receives stable relationship features derived from normalized embeddings:

- Learner-answer similarity to the reference answer.
- Maximum similarity to acceptable answers.
- Average similarity to required concepts.
- Minimum similarity to required concepts.
- Maximum similarity to common misconceptions and prohibited claims.
- Correct-evidence similarity minus misconception similarity.
- Learner/reference answer-length ratio.
- Exact normalized acceptable-answer indicator.

This representation is intentionally service-neutral. The classifier learns what complete, partial, adjacent, and incorrect semantic relationships look like instead of memorizing embedding dimensions associated with individual AWS services.

Changing feature definitions requires a new `feature_version`, retraining, validation, final evaluation, and release-note entry.

### Supervised Classification Head

The v3.0.0 head is a class-balanced multinomial logistic classifier.

The saved artifact contains:

- Ordered class labels.
- Feature normalization means and scales.
- Classifier coefficients and intercepts.
- Feature contract version.
- Encoder identity and pinned revision.
- Training-data manifest hashes.
- Validation metrics used to accept the artifact.
- Training script version or source commit.

The artifact must not contain copied learner answers, exact question-and-answer lookup keys, or final test labels.

### Deterministic Safety Rules

Small deterministic rules may surround the classifier when they express an explicit rubric invariant:

- An exact normalized acceptable answer may receive the configured full-credit floor.
- An exact normalized severe misconception or prohibited claim may receive the configured failure cap.
- Empty answers are not evaluated.

Rules must be documented and tested. They must not become a second undocumented heuristic model, and release evaluation must exercise the same rules used in production.

## Data Contract

### Versioned Training Sources

`config/data/structured_answer_training_data.json` is a versioned, human-reviewable training source. It may contain:

- Question and reference-answer metadata.
- Required concepts and acceptable answers.
- Common misconceptions and prohibited claims.
- Labeled A/B/C/D/F learner-answer examples.
- Source and rationale metadata.

Structured rows augment the training split only. They are not runtime calibration records and are not part of final verification.

### Generated Splits

- `data/generated/questions_with_answers_training.json`: model fitting.
- `data/generated/questions_with_answers_validation.json`: model selection and validation gate.
- `data/generated/questions_with_answers_test.json`: final reporting only.

Splits must be disjoint by question family or concept scenario, not merely by answer wording. Paraphrases of the same question must remain in the same split.

### Curated Feedback

Human feedback may be reviewed and promoted into a future version of the structured training source. It must not automatically become a production score override. Promotion requires:

- Label review against `docs/ANSWER_RUBRIC.md`.
- Conflict resolution.
- Source and schema validation.
- Assignment to the training pool before the next split or model version is frozen.

### Final Test Integrity

The final test split must never be used for:

- Model fitting.
- Feature selection.
- Hyperparameter selection.
- Threshold tuning.
- Training-example generation.
- Deciding which individual mistakes to patch before reporting the same release.

After final-test evaluation, changes motivated by those results require a new model candidate and a newly frozen final test set for the next release cycle.

## Training Workflow

1. Generate or validate the training, validation, and final test manifests.
2. Confirm question-family separation across all splits.
3. Download the pinned encoder files when absent.
4. Build semantic relationship features for training rows.
5. Add approved structured examples to training only.
6. Fit the supervised A/B/C/D/F head.
7. Evaluate against validation.
8. Save the candidate artifact only when the validation gate passes.
9. Run final-test evaluation once for release reporting.
10. Package the pinned encoder and accepted classifier in the release image.

The final-test script must not import or invoke training functions.

## Runtime Behavior

- Default development device: `auto`.
- Production Docker device: `cpu` through `AWS_COACH_CPU_ONLY=1`.
- Runtime network access: not required.
- Encoder and classifier load once as cached application resources.
- Every answer is transformed using the same feature contract used during training.
- Missing or incompatible model artifacts produce a controlled unavailable state; the application must not silently switch to a different grading model.

An explicit operator-configured fallback may exist for emergency recovery, but its use must be visible in logs and the learner interface and must not be reported as v3 classifier output.

## Metrics And Release Gates

Primary release metric:

- Within-one-letter accuracy on the untouched final test split.

The complete formulas, migration-comparison rules, detailed diagnostics, and JSON schema are defined in `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_METRICS.md`.

Required diagnostics:

- Validation exact-letter accuracy.
- Final-test exact-letter accuracy.
- Per-grade precision and recall.
- Confusion matrix.
- Accuracy by certification, domain, question type, and answer-length band.
- Exact acceptable-answer pass rate.
- Severe-misconception rejection rate.
- CPU model-load time and grading latency.

Release gates for v3.0.0:

- Validation within-one-letter accuracy: greater than 90%.
- Final-test within-one-letter accuracy: greater than 90%.
- Exact-letter accuracy and per-grade recall remain required published diagnostics.
- No train/validation/test question-family overlap.
- Unit and model tests pass.
- CPU production smoke test passes without network access.
- Clean-clone Docker build contains the pinned encoder and classifier.

Calibration-fit accuracy, training accuracy, and within-one-letter accuracy may appear as diagnostics but cannot replace exact final-test accuracy.

## Packaging And Reproducibility

The model download step must fetch only files needed by the PyTorch/SentenceTransformers runtime. It must not download ONNX, OpenVINO, TensorFlow, or unrelated backend variants.

The production image must be reproducible from a clean clone. Version 3 uses a versioned encoder manifest containing the Hugging Face repository, pinned revision, required-file allowlist, licenses, and checksums. The Docker build downloads only those files and verifies the manifest before creating the runtime image. The small classifier JSON is committed as a versioned release artifact.

An offline build may prefetch the same verified encoder bundle, but it must use the identical manifest. Relying on an ignored developer-local directory is not release-safe.

The container must include:

- Pinned encoder files.
- Accepted classifier artifact.
- Runtime configuration.
- App-facing questions.
- License and provenance notices required for redistribution.

## Migration From Version 2

Version 3 retires these components from production grading:

- Lexical binary classifier.
- Partial-credit regressor.
- Deterministic `semantic_similarity` as the primary scorer.
- Exact question-and-answer calibration lookups.

Legacy evaluators may remain temporarily for historical metric comparison and rollback testing. They must be clearly labeled as legacy and must not supply v3 production metrics.

The migration sequence is:

1. Train and evaluate the v3 candidate in shadow mode.
2. Complete documentation, provenance, packaging, and clean-build checks.
3. Meet all v3 release gates.
4. Switch the default evaluator to the local semantic classifier.
5. Retain one release-scoped rollback option.
6. Remove legacy runtime paths in a later cleanup after production verification.

## Acceptance Criteria

The design is implemented when:

- The production application grades with the local semantic classifier.
- Runtime grading needs no API key or network call.
- Structured examples influence training but are not runtime lookup overrides.
- Training cannot read final test data by default or through shared loaders.
- Release metrics identify the exact classifier and encoder revisions evaluated.
- Final-test within-one-letter accuracy is greater than 90%.
- A clean-clone CPU Docker image builds and grades a smoke-test answer offline.
- Documentation, release notes, architecture, configuration, and scripts describe the same model path.
