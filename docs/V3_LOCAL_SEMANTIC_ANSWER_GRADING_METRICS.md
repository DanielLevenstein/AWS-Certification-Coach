# v3.0.0 Local Semantic Answer Grading Metrics

Status: Implemented for `v3.prototype.3`
Target release: `v3.0.0`  
Applies to: Learner-answer grading  
Related documents: `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_DESIGN.md`, `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_ARCHITECTURE.md`, `docs/ANSWER_RUBRIC.md`

## Purpose

Version 3 keeps the established answer-quality columns so migration can be compared with earlier scorers, but freezes their definitions and benchmark requirements. It also adds multi-class diagnostics appropriate for a supervised A/B/C/D/F classifier.

Metric names alone do not make results comparable. A comparison is valid only when both evaluators run against the same labeled rows, split manifest, grade definitions, exclusions, and runtime guardrails.

## Grade Ordering And Bands

Ordered grade scale:

```text
A, B, C, D, F
```

Ordinal indexes used by distance metrics:

| Grade | Index |
|:------|------:|
| A | 0 |
| B | 1 |
| C | 2 |
| D | 3 |
| F | 4 |

Legacy semantic grade bands:

| Letter grades | Grade band |
|:--------------|:-----------|
| A, B | A/B |
| C, D | C/D |
| F | F |

Legacy accepted-answer diagnostic:

- Positive or accepted: `A`, `B`, `C`, or `D`.
- Negative or rejected: `F`.

These legacy groupings are retained only for migration continuity. They do not replace exact-letter grading.

## Comparable Headline Metrics

### Semantic Accuracy

Definition: fraction of examples where predicted and expected grades belong to the same legacy grade band.

```text
semantic_accuracy = matching_grade_bands / evaluated_examples
```

Examples:

- Expected A, predicted B: match.
- Expected C, predicted D: match.
- Expected B, predicted C: mismatch.
- Expected D, predicted F: mismatch.

The historical column name `Semantic Accuracy` remains in the v3 migration table. New implementation code should use the unambiguous JSON key `grade_band_accuracy` and may emit `semantic_accuracy` as a compatibility alias.

### Semantic Precision

Definition: precision of the legacy accepted-answer class, where A through D are positive and F is negative.

```text
semantic_precision = accepted_true_positive / (accepted_true_positive + accepted_false_positive)
```

An accepted false positive occurs when the expected grade is F but the model predicts A, B, C, or D.

This metric measures how trustworthy an accepted result is. It does not distinguish A from D.

### Semantic Recall

Definition: recall of the legacy accepted-answer class.

```text
semantic_recall = accepted_true_positive / (accepted_true_positive + accepted_false_negative)
```

An accepted false negative occurs when the expected grade is A, B, C, or D but the model predicts F.

This metric measures how often the model avoids rejecting answers that deserve some credit. It does not distinguish A from D.

### Exact Letter Accuracy

Definition: fraction of examples where the predicted and expected A/B/C/D/F grades are identical.

```text
exact_letter_accuracy = exact_letter_matches / evaluated_examples
```

This remains an honestly reported diagnostic. Expected A with predicted B is an exact-letter error even though it is close enough for the release tolerance.

### Within 1 Letter

Definition: fraction of examples where the absolute ordinal distance between expected and predicted grades is at most one.

```text
within_one_letter = count(abs(expected_index - predicted_index) <= 1) / evaluated_examples
```

Examples:

- Expected A, predicted B: match.
- Expected C, predicted B or D: match.
- Expected D, predicted F: match.
- Expected A, predicted C: mismatch.

Within 1 Letter is the primary v3 release gate. It must be greater than 90%. Exact-letter, per-grade, ordinal-error, and severe-error results remain visible so that this tolerance cannot hide the model's actual behavior.

## Required New Classifier Diagnostics

### Five-Class Macro Precision

Calculate precision independently for A, B, C, D, and F, then average the five values equally.

Macro precision prevents large classes from hiding poor performance on less common grades.

### Five-Class Macro Recall

Calculate recall independently for A, B, C, D, and F, then average the five values equally.

### Five-Class Macro F1

Calculate F1 independently for every grade and average the five values equally.

Macro F1 is the primary class-balance diagnostic. It is not directly comparable to the legacy binary semantic precision and recall columns.

### Per-Grade Precision And Recall

The release artifact must report precision, recall, support, and F1 for every letter grade.

Particular attention is required for:

- A recall: correct complete answers should receive full credit.
- F recall: clearly wrong answers should be rejected.
- B/C and C/D confusion: these boundaries represent most legitimate calibration difficulty.

### Ordinal Mean Absolute Error

Definition: average absolute distance between expected and predicted grade indexes.

```text
ordinal_mae = mean(abs(expected_index - predicted_index))
```

Lower is better. This metric distinguishes adjacent mistakes from severe A-to-F mistakes without replacing exact accuracy.

### Severe Error Rate

Definition: fraction of examples with an ordinal grade distance of two or more.

```text
severe_error_rate = count(abs(expected_index - predicted_index) >= 2) / evaluated_examples
```

### F Rejection Recall

Definition: fraction of expected-F examples predicted as F.

```text
f_rejection_recall = expected_f_predicted_f / expected_f_examples
```

This is the clearest learner-safety diagnostic for confidently accepting wrong answers.

### Confusion Matrix

Every validation and final-test report must include a complete 5x5 confusion matrix with expected grades as rows and predicted grades as columns.

## Optional Probability Diagnostics

When the classifier exposes class probabilities, reports may also include:

- Multi-class log loss.
- Brier score.
- Expected calibration error.
- Reliability plots.

These diagnose confidence quality, not grading correctness. They are not v3.0.0 headline release metrics.

## Benchmark Contract

### Migration Benchmark

The old production scorer and the v3 candidate must both run against the same frozen migration benchmark.

The comparison must use:

- Identical question rows and learner answers.
- Identical expected A/B/C/D/F labels.
- Identical conflict exclusions.
- Identical grade conversion and ordering.
- Each evaluator's real production guardrails.
- No use of benchmark labels as runtime calibrations.

If the legacy evaluator loads a curated calibration store, the report must include its calibration-hit count. Migration benchmark rows that are exact calibration keys invalidate a generalization comparison and must be removed or placed in a separately labeled calibration-fit report.

### Final Test Benchmark

The v3 final test split is used only for final reporting. It must remain disjoint from:

- Generated training questions.
- Generated validation questions.
- Structured training examples.
- Curated rows promoted into training.
- Paraphrases from the same question family.

The report must record the benchmark manifest hash, example count, class support, and question-family count.

### Historical Comparability

Historical release-table values remain historical facts, but they are not automatically comparable to v3 when their datasets or calibration behavior differ.

The v3 release report must include a side-by-side migration section produced by rerunning the legacy and v3 scorers on the frozen v3 migration benchmark. Historical values should not be recomputed or silently overwritten.

## Evaluation Slices

The final report must provide exact accuracy and support for:

- Grade.
- Certification.
- Domain.
- Question type.
- Answer-length band.
- Exact acceptable answer versus paraphrase.
- Correct-service concise answer versus reasoned answer.
- Adjacent-service answer.
- Severe misconception answer.
- Questions with one required concept versus multiple required concepts.

A slice with too few examples must be labeled insufficient rather than interpreted as a stable percentage.

## Metric Edge Cases

- Conflicting expected labels are excluded from benchmark scoring and reported separately.
- Empty benchmark sets are errors, not zero-percent results.
- Precision with no predicted positives is reported as undefined and fails the relevant gate.
- Recall with no expected positives is reported as undefined and marks the benchmark invalid for that metric.
- Every grade must have non-zero support for macro metrics.
- Duplicate normalized question-and-answer rows count once unless the benchmark explicitly defines weighted sampling.
- Runtime exceptions count as incorrect predictions and are also reported separately.

## v3.0.0 Release Table

The migration-friendly release table keeps the established columns:

| Release | Evaluator | Benchmark | Semantic Accuracy | Semantic Precision | Semantic Recall | Exact Letter Accuracy | Within 1 Letter |
|:--------|:----------|:----------|------------------:|-------------------:|----------------:|----------------------:|----------------:|
| v3.0.0 candidate | local semantic classifier | `<manifest>` | TBD | TBD | TBD | TBD | TBD |

Question Fidelity remains in its own question-quality table or a clearly separated column group. It is not an answer-model metric.

The detailed classifier table adds:

| Evaluator | Macro Precision | Macro Recall | Macro F1 | Ordinal MAE | Severe Error Rate | F Rejection Recall |
|:----------|----------------:|-------------:|---------:|------------:|------------------:|-------------------:|
| local semantic classifier | TBD | TBD | TBD | TBD | TBD | TBD |

## Release Gate

Hard gates:

- Within 1 Letter: greater than 90%.
- Every grade has sufficient benchmark support.
- Split-integrity and benchmark-manifest checks pass.

Migration comparison diagnostics:

- The v3 candidate must exceed the legacy evaluator's Exact Letter Accuracy on the same benchmark.
- Semantic Accuracy, Precision, and Recall may not regress by more than two percentage points without an explicit reviewed rationale.
- Any improvement caused only by exact calibration hits must be labeled calibration fit and excluded from the generalization claim.

Exact-letter accuracy, macro F1, per-grade recall, severe-error rate, and migration deltas are published diagnostics rather than release blockers. This favors a generalizing evaluator whose predictions remain close to the reviewed grade over a calibration lookup that appears exact only because it has seen the evaluation row.

## JSON Metrics Contract

The final evaluator writes stable keys:

```json
{
  "metrics_schema_version": 3,
  "evaluator": {
    "name": "semantic_grade_classifier_v1",
    "feature_version": "semantic-relations-v2",
    "encoder_repository": "sentence-transformers/all-MiniLM-L6-v2",
    "encoder_revision": "<pinned-revision>"
  },
  "benchmark": {
    "name": "v3_final_test",
    "manifest_sha256": "<sha256>",
    "example_count": 0,
    "question_family_count": 0,
    "support_by_grade": {}
  },
  "metrics": {
    "grade_band_accuracy": 0.0,
    "semantic_accuracy": 0.0,
    "semantic_precision": 0.0,
    "semantic_recall": 0.0,
    "exact_letter_accuracy": 0.0,
    "within_one_letter_accuracy": 0.0,
    "macro_precision": 0.0,
    "macro_recall": 0.0,
    "macro_f1": 0.0,
    "ordinal_mae": 0.0,
    "severe_error_rate": 0.0,
    "f_rejection_recall": 0.0
  },
  "per_grade": {},
  "confusion_matrix": {},
  "slices": {},
  "runtime_errors": []
}
```

`semantic_accuracy` is a compatibility alias for `grade_band_accuracy`; both values must be identical.

## Validation Versus Final Reporting

Validation reports use the same metric formulas but are labeled `validation`. They may guide model selection.

Final-test reports are labeled `final_test`. They may determine release readiness but may not guide another training iteration against the same frozen test set.

Training-set metrics are optional diagnostics and are never included in the release headline table.

## Acceptance Criteria

The metrics contract is implemented when:

- One evaluator function computes all shared metrics from expected and predicted letter grades.
- Legacy and v3 scorers can be evaluated side by side on the same benchmark.
- Existing release-column definitions are preserved exactly.
- Within-one-letter accuracy greater than 90% is the primary v3 gate.
- Macro and per-grade metrics expose class imbalance.
- Reports include benchmark and model provenance.
- Test labels are unavailable to training and feature-selection code.
- Release notes render the migration table and detailed classifier table without mixing question-fidelity metrics into answer-model claims.

## Prototype Milestone Status

`v3.prototype.3` freezes the formulas in
`src/aws_certification_coach/model_evaluation/grade_metrics.py`, the schema-v3 final-test
artifact, and the release thresholds above. `scripts/evaluate_semantic_answer_classifier.py`
enforces the complete gate set by default; `--report-only` is reserved for diagnostic runs
that must be clearly treated as non-release results.
