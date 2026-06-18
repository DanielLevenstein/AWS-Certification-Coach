# Heuristic Scoring Rubric

Use this rubric to design question-fidelity scoring for generated AWS certification questions. Keep it separate from learner-answer scoring.

## Recommended Dimensions

| Dimension             | Suggested Weight | Purpose                                                                                                              |
|:----------------------|-----------------:|:---------------------------------------------------------------------------------------------------------------------|
| Concept fidelity      |               35 | Generated question tests the same AWS concept, service boundary, and decision point as the source set.               |
| Exam-style fidelity   |               25 | Scenario shape, reasoning depth, and prompt framing resemble permitted AWS Developer Associate calibration examples. |
| Distractor quality    |               15 | Wrong options are plausible AWS services/features and expose the intended misconception.                             |
| Technical correctness |               15 | Reference answer and explanation are accurate according to AWS documentation.                                        |
| Source safety         |               10 | Generated text is self-authored and does not copy restricted or official practice text.                              |

Scores should be reported as a percentage value. If separate metrics are clearer, use `question concept fidelity` and `question exam-style fidelity` instead of hiding both behind one number.

## Hard Rejection Rules

Reject a generated question regardless of weighted score when:

- It copies restricted question text or answer explanations.
- It points to the wrong AWS service or feature.
- It tests a different certification domain than the source target.
- It is only factual trivia and lacks Developer Associate-style applied reasoning.
- Its correct answer is ambiguous between multiple AWS services.
- Its distractors are obviously unrelated or nonsensical.

## Evidence To Include

For each score, require short evidence fields:

- `covered_concepts`
- `missing_concepts`
- `conflicting_concepts`
- `matched_exam_style_pattern`
- `distractor_notes`
- `copying_risk_notes`
- `review_recommendation`: `accept`, `revise`, or `reject`

## Threshold Guidance

- `90-100`: Strong candidate; still sample-review before release.
- `80-89`: Acceptable if human review confirms exam-style fit.
- `70-79`: Revise before release unless intentionally used as a diagnostic borderline example.
- `<70`: Reject from app-facing generated question bank.

Do not tune thresholds against final test data.
