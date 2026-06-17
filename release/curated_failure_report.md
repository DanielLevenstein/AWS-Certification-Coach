# Curated Grade Failure Report

- Curated examples: 23
- Evaluation bands: `A/B`, `C/D`, `F`
- Passing grade-band predictions: 18
- Failing grade-band predictions: 5
- Grade-band accuracy: 78.26%
- Unique failing question/answer/grade cases: 5
- Conflicting normalized label sets: 0
- Actual grade bands among failures: {'C/D': 3, 'F': 2}

## Primary Findings

1. Generated-label training error is low; remaining app-scoring failures are now `semantic_similarity` calibration cases rather than epoch-count issues.
2. The `semantic_similarity` model recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.
3. Full-credit prose is scored through service and concept coverage rather than only exact option text.
4. No cross-band duplicate-label conflicts were detected in the curated data.

## Label Conflicts

- None detected.

## Failing Cases

### 1. Expected F, received C/D

- Rows: `14`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.
- Expected rating: `0.25`
- User answer: `S3 version tracking`
- Correct answer: S3 lifecycle policies
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 2. Expected C/D, received F

- Rows: `1`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to set maximum available permissions across accounts in an AWS Organization.
- Expected rating: `0.65`
- User answer: `AWS Roles`
- Correct answer: Service Control Policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 3. Expected C/D, received F

- Rows: `2`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.65`
- User answer: `AWS Key Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 4. Expected A/B, received C/D

- Rows: `10`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Expected rating: `0.85`
- User answer: `AWS Cost Center`
- Correct answer: AWS Budgets
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 5. Expected F, received C/D

- Rows: `9`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to track resource configuration history and evaluate compliance against rules.
- Expected rating: `0.25`
- User answer: `AWS Compliance Manager`
- Correct answer: AWS Config
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

## Recommended Remediation Order

1. Reconcile conflicting curated labels before changing model code.
2. Expand normalized AWS service aliases and near-service synonym handling.
3. Tune concept-coverage thresholds against curated examples.
4. Keep generated-label regression metrics out of release tracking unless the trained model returns to the app path.
5. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.

