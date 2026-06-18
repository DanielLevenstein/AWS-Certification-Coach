# Curated Grade Failure Report

- Curated examples: 32
- Evaluation grades: `A`, `B`, `C`, `D`, `F`
- Passing exact-letter predictions: 15
- Failing exact-letter predictions: 17
- Exact-letter accuracy: 46.88%
- Unique failing question/answer/grade cases: 14
- Conflicting normalized label sets: 0
- Actual letter grades among failures: {'B': 5, 'C': 2, 'D': 8, 'F': 2}

## Primary Findings

1. Generated-label training error is low; remaining app-scoring failures are now `semantic_similarity` calibration cases rather than epoch-count issues.
2. The `semantic_similarity` model recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.
3. Full-credit prose is scored through service and concept coverage rather than only exact option text.
4. No exact-letter duplicate-label conflicts were detected in the curated data.

## Label Conflicts

- None detected.

## Failing Cases

### 1. Expected A, received F

- Rows: `26`; occurrences: `1`
- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Expected rating: `0.95`
- User answer: `AWS Code Build`
- Correct answer: a CodeBuild buildspec file
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Reviewer feedback: Again my answer is correct. Are you sure you are using the semantic evaluation logic?
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 2. Expected C, received D

- Rows: `20, 30`; occurrences: `2`
- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Expected rating: `0.75`
- User answer: `AWS KMS Keys`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Reviewer feedback: We should update the grading model to give partial credit to the best near miss answer. Near miss answers can be determined by having words like only or alone in the answer selection.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 3. Expected A, received B

- Rows: `25`; occurrences: `1`
- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Expected rating: `0.95`
- User answer: `DynamoDB Time to Live can be used to remove old DynamoDB sections with a scheduled cleanup job.`
- Correct answer: Enable DynamoDB Time to Live
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: This answer covers the expected AWS concepts.
- Reviewer feedback: This is a full answer it's just worded slightly differently
- Largest feature contributions: `semantic_similarity_score` +0.840
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 4. Expected C, received B

- Rows: `28`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.75`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.840
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 5. Expected C, received B

- Rows: `27`; occurrences: `1`
- Question: An SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message?
- Expected rating: `0.75`
- User answer: `SQS FILO queue`
- Correct answer: Adjust the SQS visibility timeout
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: This answer covers the expected AWS concepts.
- Reviewer feedback: My answer had nothing to do with the cannon answer but might still be partially right.
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

### 8. Expected A, received D

- Rows: `29`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.95`
- User answer: `AWS Kenesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: The AWS service name appears to be misspelled.
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Runtime spelling guard assigned a fixed D-range score; the expected grade disagrees with that policy.

### 9. Expected C, received D

- Rows: `10`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.
- Expected rating: `0.75`
- User answer: `route 55`
- Correct answer: Amazon Route 53
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 10. Expected C, received D

- Rows: `11`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Expected rating: `0.75`
- User answer: `Allow and deny rules`
- Correct answer: network ACLs
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 11. Expected A, received C

- Rows: `22, 24`; occurrences: `2`
- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Expected rating: `0.95`
- User answer: `AWS Cloud trail is used to record AWS API activity for auditing.`
- Correct answer: AWS CloudTrail
- Raw model score: `72.00`; runtime score: `72`
- Runtime feedback: This answer covers the expected AWS concepts.
- Reviewer feedback: I entered a freeform version of the correct answer.
- Largest feature contributions: `semantic_similarity_score` +0.720
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 12. Expected C, received D

- Rows: `21, 31`; occurrences: `2`
- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Expected rating: `0.75`
- User answer: `RDS read replicas can be used for low-latency data synchronization across multiple availability zones.`
- Correct answer: DynamoDB global tables
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Reviewer feedback: We need to decide in our design rubric if we are giving partial credit answers a score of Grade D or Grade C
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 13. Expected F, received D

- Rows: `13`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.25`
- User answer: `Parameter Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 14. Expected B, received F

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

