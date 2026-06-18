# Curated Grade Failure Report

- Curated examples: 40
- Evaluation grades: `A`, `B`, `C`, `D`, `F`
- Passing exact-letter predictions: 22
- Failing exact-letter predictions: 18
- Exact-letter accuracy: 55.00%
- Unique failing question/answer/grade cases: 13
- Conflicting normalized label sets: 2
- Actual letter grades among failures: {'B': 6, 'D': 10, 'F': 2}

## Primary Findings

1. Generated-label training error is low; remaining app-scoring failures are now `semantic_similarity` calibration cases rather than epoch-count issues.
2. The `semantic_similarity` model recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.
3. Full-credit prose is scored through service and concept coverage rather than only exact option text.
4. At least one normalized question/answer pair has contradictory curated grades, making perfect accuracy impossible until labels are reconciled.

## Label Conflicts

- Question: `a developer must keep application database passwords out of code and periodically replace them without a manual handoff which aws service should manage this credential lifecycle`; answer: `aws kms keys`; grades: `C, F`
- Question: `explain which aws service or feature should be used to ingest and process real time streaming data at scale`; answer: `aws kinesis`; grades: `A, B`

## Failing Cases

### 1. Expected A, received B

- Rows: `26`; occurrences: `1`
- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Expected rating: `0.95`
- User answer: `AWS Code Build`
- Correct answer: a CodeBuild buildspec file
- Raw model score: `80.00`; runtime score: `80`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.800
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 2. Expected F, received D

- Rows: `20, 30, 33`; occurrences: `3`
- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Expected rating: `0.25`
- User answer: `AWS KMS Keys`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 3. Expected C, received D

- Rows: `37`; occurrences: `1`
- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Expected rating: `0.75`
- User answer: `AWS KMS Keys`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 4. Expected A, received B

- Rows: `25`; occurrences: `1`
- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Expected rating: `0.95`
- User answer: `DynamoDB Time to Live can be used to remove old DynamoDB sections with a scheduled cleanup job.`
- Correct answer: Enable DynamoDB Time to Live
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.840
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 5. Expected C, received B

- Rows: `27`; occurrences: `1`
- Question: An SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message?
- Expected rating: `0.75`
- User answer: `SQS FILO queue`
- Correct answer: Adjust the SQS visibility timeout
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.840
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 6. Expected A, received B

- Rows: `17`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.95`
- User answer: `AWS KMS creates and manages encryption keys that protect data.`
- Correct answer: AWS KMS
- Raw model score: `88.00`; runtime score: `88`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.880
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 7. Expected A, received B

- Rows: `18`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.95`
- User answer: `AWS KMS manages encryption keys.`
- Correct answer: AWS KMS
- Raw model score: `88.00`; runtime score: `88`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.880
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 8. Expected A, received B

- Rows: `29`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.95`
- User answer: `AWS Kinesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `80.00`; runtime score: `80`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.800
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 9. Expected C, received D

- Rows: `11`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Expected rating: `0.75`
- User answer: `Allow and deny rules`
- Correct answer: network ACLs
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 10. Expected C, received D

- Rows: `21, 31, 34, 38`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Expected rating: `0.75`
- User answer: `RDS read replicas can be used for low-latency data synchronization across multiple availability zones.`
- Correct answer: DynamoDB global tables
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 11. Expected A, received F

- Rows: `5`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Expected rating: `0.95`
- User answer: `route 53`
- Correct answer: Amazon EventBridge
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 12. Expected F, received D

- Rows: `13`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.25`
- User answer: `Parameter Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 13. Expected B, received F

- Rows: `9`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Expected rating: `0.85`
- User answer: `AWS Cost Center`
- Correct answer: AWS Budgets
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

## Recommended Remediation Order

1. Reconcile conflicting curated labels before changing model code.
2. Expand normalized AWS service aliases and near-service synonym handling.
3. Tune concept-coverage thresholds against curated examples.
4. Keep generated-label regression metrics out of release tracking unless the trained model returns to the app path.
5. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.

