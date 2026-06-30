# Curated Grade Failure Report

- Curated examples: 106
- Evaluation grades: `A`, `B`, `C`, `D`, `F`
- Passing exact-letter predictions: 69
- Failing exact-letter predictions: 37
- Exact-letter accuracy: 65.09%
- Unique failing question/answer/grade cases: 37
- Conflicting normalized label sets: 3
- Actual letter grades among failures: {'C': 6, 'D': 5, 'F': 26}

## Primary Findings

1. Remaining app-scoring failures are `semantic_similarity` calibration cases.
2. The `semantic_similarity` model recognizes service aliases and concept coverage, but it still uses deterministic rules that miss some AWS synonym and near-service cases.
3. Full-credit prose is scored through service and concept coverage rather than only exact option text.
4. At least one normalized question/answer pair has contradictory curated grades, making perfect accuracy impossible until labels are reconciled.

## Label Conflicts

- Question: `a team exposes a lambda backed rest api and must run custom token validation before requests reach the backend function which api gateway feature should the developer configure`; answer: `which api gateway feature should be used to run token validation on requests`; grades: `D, F`
- Question: `an sns topic publishes all order events but each subscribed queue should receive only messages for selected order types based on attributes which sns feature should the developer configure`; answer: `sns topics allow multiple receivers to see the same queue but i don t think it allows filtering based on attributes so i am going to have to go with i don t know`; grades: `B, C`
- Question: `explain which aws service or feature should be used to ingest and process real time streaming data at scale`; answer: `aws kinesis`; grades: `A, B`

## Failing Cases

### 1. Expected A, received C

- Rows: `71`; occurrences: `1`
- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Expected rating: `0.95`
- User answer: `AWS Code Build`
- Correct answer: a CodeBuild buildspec file
- Raw model score: `79.00`; runtime score: `79`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Reviewer feedback: Again my answer is correct. Are you sure you are using the semantic evaluation logic?
- Largest feature contributions: `semantic_similarity_score` +0.790
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 2. Expected C, received F

- Rows: `14`; occurrences: `1`
- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Expected rating: `0.75`
- User answer: `Use DynamoDB automatic expiration.`
- Correct answer: Enable DynamoDB Time to Live
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: This exact service answer is not in the question's correct answer list.
- Reviewer feedback: Balanced grade example: names DynamoDB and automatic expiration but does not identify TTL or the timestamp attribute.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered.

### 3. Expected F, received D

- Rows: `76`; occurrences: `1`
- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Expected rating: `0.25`
- User answer: `Which API Gateway feature should be used to run token validation on requests?`
- Correct answer: an API Gateway Lambda authorizer
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 4. Expected C, received D

- Rows: `75`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.75`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 5. Expected B, received D

- Rows: `73`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.85`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 6. Expected C, received F

- Rows: `15`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.75`
- User answer: `Use SNS attributes for order types.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: This exact service answer is not in the question's correct answer list.
- Reviewer feedback: Balanced grade example: recognizes SNS attributes and order-type routing but misses subscription filter policies.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered.

### 7. Expected D, received F

- Rows: `102`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to act as stateful virtual firewalls controlling inbound and outbound traffic for resources.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to act as stateful virtual firewalls controlling inbound and outbound traffic for resources.`
- Correct answer: VPC security groups
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 8. Expected C, received D

- Rows: `85`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.
- Expected rating: `0.75`
- User answer: `Elastic load balancing is a way of automatically adjusting demand based on health checks.`
- Correct answer: Auto Scaling groups
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Reviewer feedback: Elastic Load balancing is a sub feature of auto scaling groups
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 9. Expected D, received F

- Rows: `97`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.`
- Correct answer: Auto Scaling groups
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 10. Expected D, received F

- Rows: `90`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.`
- Correct answer: S3 lifecycle policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 11. Expected D, received F

- Rows: `100`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to cache and deliver content from edge locations to reduce latency for users.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to cache and deliver content from edge locations to reduce latency for users.`
- Correct answer: Amazon CloudFront
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 12. Expected D, received F

- Rows: `105`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to collect metrics, logs, alarms, and dashboards for monitoring AWS resources.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to collect metrics, logs, alarms, and dashboards for monitoring AWS resources.`
- Correct answer: Amazon CloudWatch
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 13. Expected C, received F

- Rows: `16`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to collect metrics, logs, alarms, and dashboards for monitoring AWS resources.
- Expected rating: `0.75`
- User answer: `Use metrics and alarms.`
- Correct answer: Amazon CloudWatch
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: This exact service answer is not in the question's correct answer list.
- Reviewer feedback: Balanced grade example: mentions key monitoring outputs but omits CloudWatch and the full monitoring scope.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered.

### 14. Expected C, received F

- Rows: `79`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.75`
- User answer: `Encryption keys protect data in AWS services.`
- Correct answer: AWS KMS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Letter-grade verification answer: covers the security domain and key concepts but misses the AWS KMS service name, so it should receive C.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 15. Expected D, received F

- Rows: `99`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to distribute traffic across healthy targets to improve availability and scalability.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to distribute traffic across healthy targets to improve availability and scalability.`
- Correct answer: Elastic Load Balancing
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 16. Expected D, received F

- Rows: `86`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to grant temporary credentials to trusted AWS resources without storing long-term access keys.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to grant temporary credentials to trusted AWS resources without storing long-term access keys.`
- Correct answer: IAM roles
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 17. Expected D, received F

- Rows: `98`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to horizontally scale an EC2 application by adding and replacing instances automatically instead of manually moving to a larger instance type.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to horizontally scale an EC2 application by adding and replacing instances automatically instead of manually moving to a larger instance type.`
- Correct answer: Auto Scaling groups
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 18. Expected D, received F

- Rows: `88`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to improve high availability and fault tolerance during an Availability Zone impairment.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to improve high availability and fault tolerance during an Availability Zone impairment.`
- Correct answer: multiple Availability Zones
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 19. Expected B, received C

- Rows: `52`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.85`
- User answer: `AWS Kinesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `75.00`; runtime score: `75`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Largest feature contributions: `semantic_similarity_score` +0.750
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 20. Expected A, received C

- Rows: `74`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.95`
- User answer: `AWS Kinesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `75.00`; runtime score: `75`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Largest feature contributions: `semantic_similarity_score` +0.750
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 21. Expected D, received F

- Rows: `89`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to preserve, retrieve, and restore previous versions of objects after overwrite or delete events.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to preserve, retrieve, and restore previous versions of objects after overwrite or delete events.`
- Correct answer: Amazon S3 versioning
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 22. Expected D, received F

- Rows: `94`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide a fully managed NoSQL key-value and document database with low-latency access.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide a fully managed NoSQL key-value and document database with low-latency access.`
- Correct answer: Amazon DynamoDB
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 23. Expected D, received F

- Rows: `101`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.`
- Correct answer: Amazon Route 53
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 24. Expected D, received F

- Rows: `103`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.`
- Correct answer: network ACLs
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 25. Expected D, received F

- Rows: `92`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide synchronous standby replication and automatic failover for relational databases.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide synchronous standby replication and automatic failover for relational databases.`
- Correct answer: Amazon RDS Multi-AZ
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 26. Expected A, received C

- Rows: `69`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Expected rating: `0.95`
- User answer: `AWS Cloud trail is used to record AWS API activity for auditing.`
- Correct answer: AWS CloudTrail
- Raw model score: `79.00`; runtime score: `79`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Reviewer feedback: I entered a freeform version of the correct answer.
- Largest feature contributions: `semantic_similarity_score` +0.790
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 27. Expected D, received F

- Rows: `104`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.`
- Correct answer: AWS CloudTrail
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 28. Expected D, received F

- Rows: `95`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.`
- Correct answer: DynamoDB global tables
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 29. Expected D, received F

- Rows: `53`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Expected rating: `0.65`
- User answer: `route 53`
- Correct answer: Amazon EventBridge
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 30. Expected D, received F

- Rows: `96`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to run event-driven code without managing servers and scale per request.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to run event-driven code without managing servers and scale per request.`
- Correct answer: AWS Lambda
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 31. Expected D, received F

- Rows: `93`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to scale read-heavy database workloads by serving read traffic from replicated database instances.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to scale read-heavy database workloads by serving read traffic from replicated database instances.`
- Correct answer: Amazon RDS read replicas
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 32. Expected B, received C

- Rows: `51`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store rarely accessed archival data at lower cost with retrieval-time tradeoffs.
- Expected rating: `0.85`
- User answer: `AWS Glacier`
- Correct answer: S3 Glacier storage classes
- Raw model score: `79.00`; runtime score: `79`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Largest feature contributions: `semantic_similarity_score` +0.790
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 33. Expected D, received F

- Rows: `50`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.65`
- User answer: `AWS Key Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 34. Expected B, received C

- Rows: `57`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Expected rating: `0.85`
- User answer: `AWS Cost Center`
- Correct answer: AWS Budgets
- Raw model score: `79.00`; runtime score: `79`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Largest feature contributions: `semantic_similarity_score` +0.790
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 35. Expected D, received F

- Rows: `87`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.`
- Correct answer: AWS Budgets
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 36. Expected D, received F

- Rows: `91`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to transition old S3 objects to lower-cost storage classes and expire them after a retention period without changing bucket access permissions.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to transition old S3 objects to lower-cost storage classes and expire them after a retention period without changing bucket access permissions.`
- Correct answer: S3 lifecycle policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 37. Expected A, received D

- Rows: `84`; occurrences: `1`
- Question: Review the IAM policy for the Lambda execution role. What is the access-control issue, and what change best matches least privilege?
- Expected rating: `0.95`
- User answer: `Change resource to 
"Resource": "s3://example-bucket/reports/*"`
- Correct answer: Restrict the Resource to arn:aws:s3:::example-bucket/reports/*
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: Name the specific AWS service or feature required by the question.
- Reviewer feedback: My answer exactly matches the proposed code block.
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

## Recommended Remediation Order

1. Reconcile conflicting curated labels before changing model code.
2. Expand normalized AWS service aliases and near-service synonym handling.
3. Tune concept-coverage thresholds against curated examples.
4. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.

