# Curated Grade Failure Report

- Curated examples: 39
- Evaluation grades: `A`, `B`, `C`, `D`, `F`
- Passing exact-letter predictions: 31
- Failing exact-letter predictions: 8
- Exact-letter accuracy: 79.49%
- Unique failing question/answer/grade cases: 8
- Conflicting normalized label sets: 3
- Actual letter grades among failures: {'A': 3, 'B': 2, 'D': 1, 'F': 2}

## Primary Findings

1. Generated-label training error is low; remaining app-scoring failures are now `semantic_similarity` calibration cases rather than epoch-count issues.
2. The `semantic_similarity` model recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.
3. Full-credit prose is scored through service and concept coverage rather than only exact option text.
4. At least one normalized question/answer pair has contradictory curated grades, making perfect accuracy impossible until labels are reconciled.

## Label Conflicts

- Question: `an sns topic publishes all order events but each subscribed queue should receive only messages for selected order types based on attributes which sns feature should the developer configure`; answer: `sns topics allow multiple receivers to see the same queue but i don t think it allows filtering based on attributes so i am going to have to go with i don t know`; grades: `B, C`
- Question: `explain which aws service or feature should be used to ingest and process real time streaming data at scale`; answer: `aws kinesis`; grades: `A, B`
- Question: `explain which aws service or feature should be used to replicate tables across regions for low latency multi region access and resilience`; answer: `rds read replicas can be used for low latency data synchronization across multiple availability zones`; grades: `C, D`

## Failing Cases

### 1. Expected C, received A

- Rows: `32`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.75`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `90.00`; runtime score: `90`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.900
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 2. Expected B, received A

- Rows: `28`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.85`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `90.00`; runtime score: `90`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.900
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 3. Expected C, received B

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

### 4. Expected B, received A

- Rows: `16`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.85`
- User answer: `AWS KMS`
- Correct answer: AWS KMS
- Raw model score: `95.00`; runtime score: `95`
- Runtime feedback: This answer covers the expected AWS concepts.
- Largest feature contributions: `semantic_similarity_score` +0.950
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 5. Expected A, received B

- Rows: `29`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.95`
- User answer: `AWS Kinesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `80.00`; runtime score: `80`
- Runtime feedback: This answer covers the expected AWS concepts.
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Largest feature contributions: `semantic_similarity_score` +0.800
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 6. Expected C, received D

- Rows: `35`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Expected rating: `0.75`
- User answer: `RDS read replicas can be used for low-latency data synchronization across multiple availability zones.`
- Correct answer: DynamoDB global tables
- Raw model score: `62.00`; runtime score: `62`
- Runtime feedback: This answer needs more AWS-specific detail.
- Reviewer feedback: We need to decide in our design rubric if we are giving partial credit answers a score of Grade D or Grade C
- Largest feature contributions: `semantic_similarity_score` +0.620
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 7. Expected D, received F

- Rows: `5`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Expected rating: `0.65`
- User answer: `route 53`
- Correct answer: Amazon EventBridge
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer needs more AWS-specific detail.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 8. Expected D, received F

- Rows: `2`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.65`
- User answer: `AWS Key Store`
- Correct answer: AWS Secrets Manager
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

