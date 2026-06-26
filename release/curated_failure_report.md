# Curated Grade Failure Report

- Curated examples: 255
- Evaluation grades: `A`, `B`, `C`, `D`, `F`
- Passing exact-letter predictions: 44
- Failing exact-letter predictions: 211
- Exact-letter accuracy: 17.25%
- Unique failing question/answer/grade cases: 91
- Conflicting normalized label sets: 3
- Actual letter grades among failures: {'B': 2, 'D': 4, 'F': 205}

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

### 1. Expected D, received F

- Rows: `250`; occurrences: `1`
- Question: A CI pipeline pushes application container images to Amazon ECR, and security wants vulnerability findings before promotion to production. Which ECR capability should be enabled?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a CI pipeline pushes application container images to Amazon ECR, and security wants vulnerability findings before promotion to production. Which ECR capability should be enabled.`
- Correct answer: Enable Amazon ECR image scanning
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 2. Expected D, received F

- Rows: `244`; occurrences: `1`
- Question: A CodeBuild project runs unit tests and the team wants test case results visible in CodeBuild instead of only raw log output. What should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a CodeBuild project runs unit tests and the team wants test case results visible in CodeBuild instead of only raw log output. What should the developer configure.`
- Correct answer: Configure a CodeBuild report group
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 3. Expected D, received F

- Rows: `235`; occurrences: `1`
- Question: A DynamoDB table is keyed by customer ID, but the application now needs fast lookups by order status without scanning every item. What should the developer add to support this access pattern?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a DynamoDB table is keyed by customer ID, but the application now needs fast lookups by order status without scanning every item. What should the developer add to support this access pattern.`
- Correct answer: Add a DynamoDB secondary index
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 4. Expected D, received F

- Rows: `245`; occurrences: `1`
- Question: A Lambda application writes JSON logs to CloudWatch Logs, and a developer needs to search recent log groups for common error codes and counts. Which CloudWatch capability should be used?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a Lambda application writes JSON logs to CloudWatch Logs, and a developer needs to search recent log groups for common error codes and counts. Which CloudWatch capability should be used.`
- Correct answer: CloudWatch Logs Insights
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 5. Expected D, received F

- Rows: `222`; occurrences: `1`
- Question: A Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime.`
- Correct answer: Lambda environment variables
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 6. Expected B, received F

- Rows: `48`; occurrences: `1`
- Question: A Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime?
- Expected rating: `0.85`
- User answer: `Use environmental variables`
- Correct answer: Lambda environment variables
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: This exact service answer is not in the question's correct answer list.
- Reviewer feedback: The correct answer was to use lambda environmental variables while I said to use environmental variables.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered.

### 7. Expected D, received F

- Rows: `217`; occurrences: `1`
- Question: A Lambda function processes messages from an SQS queue. A few messages repeatedly fail and delay later processing. Which configuration should the developer use to isolate failed messages while allowing successful messages to continue?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a Lambda function processes messages from an SQS queue. A few messages repeatedly fail and delay later processing. Which configuration should the developer use to isolate failed messages while allowing successful messages to continue.`
- Correct answer: Configure an SQS dead-letter queue
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 8. Expected D, received F

- Rows: `231`; occurrences: `1`
- Question: A REST API release should expose a new deployment to 10 percent of callers while most clients continue using the current API stage. Which API Gateway deployment feature fits this rollout?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a REST API release should expose a new deployment to 10 percent of callers while most clients continue using the current API stage. Which API Gateway deployment feature fits this rollout.`
- Correct answer: an API Gateway canary release
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 9. Expected D, received F

- Rows: `248`; occurrences: `1`
- Question: A Step Functions workflow calls several Lambda tasks and should retry transient errors, then move to a compensating path when retries are exhausted. What should the developer define in the state machine?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a Step Functions workflow calls several Lambda tasks and should retry transient errors, then move to a compensating path when retries are exhausted. What should the developer define in the state machine.`
- Correct answer: Define Step Functions Retry and Catch handlers
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 10. Expected D, received F

- Rows: `239`; occurrences: `1`
- Question: A client application uploads multi-gigabyte files to S3 over an unreliable network and needs to retry only the failed pieces instead of restarting the whole upload. Which S3 upload method should it use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a client application uploads multi-gigabyte files to S3 over an unreliable network and needs to retry only the failed pieces instead of restarting the whole upload. Which S3 upload method should it use.`
- Correct answer: S3 multipart upload
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 11. Expected A, received B

- Rows: `25`; occurrences: `1`
- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Expected rating: `0.95`
- User answer: `AWS Code Build`
- Correct answer: a CodeBuild buildspec file
- Raw model score: `85.00`; runtime score: `85`
- Runtime feedback: Please write full sentence answers for full credit.
- Reviewer feedback: Again my answer is correct. Are you sure you are using the semantic evaluation logic?
- Largest feature contributions: `semantic_similarity_score` +0.850
- Suspected cause: Semantically correct prose is not an exact option-text match. The model relies on lexical containment and does not receive the runtime 95-point exact-option boost.

### 12. Expected D, received F

- Rows: `227`; occurrences: `1`
- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases.`
- Correct answer: a CodeBuild buildspec file
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 13. Expected D, received F

- Rows: `246`; occurrences: `1`
- Question: A developer instruments an application with X-Ray and needs to filter traces by tenant ID in the X-Ray console. Which kind of trace data should the code add?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a developer instruments an application with X-Ray and needs to filter traces by tenant ID in the X-Ray console. Which kind of trace data should the code add.`
- Correct answer: Add X-Ray annotations
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 14. Expected D, received F

- Rows: `223`; occurrences: `1`
- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle.`
- Correct answer: AWS Secrets Manager
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 15. Expected D, received F

- Rows: `220`; occurrences: `1`
- Question: A development team wants its release pipeline to compile code and run unit tests automatically before deployment. Which AWS service should be added as the build action?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a development team wants its release pipeline to compile code and run unit tests automatically before deployment. Which AWS service should be added as the build action.`
- Correct answer: AWS CodeBuild
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 16. Expected D, received F

- Rows: `242`; occurrences: `1`
- Question: A mobile application needs managed sign-up, sign-in, password recovery, and tokens for its end users. Which Cognito feature should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a mobile application needs managed sign-up, sign-in, password recovery, and tokens for its end users. Which Cognito feature should the developer configure.`
- Correct answer: Configure an Amazon Cognito user pool
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 17. Expected D, received F

- Rows: `232`; occurrences: `1`
- Question: A partner-facing API needs different request quotas for each client application, and callers will include API keys. Which API Gateway configuration should the developer create?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a partner-facing API needs different request quotas for each client application, and callers will include API keys. Which API Gateway configuration should the developer create.`
- Correct answer: Create an API Gateway usage plan with API keys
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 18. Expected D, received F

- Rows: `236`; occurrences: `1`
- Question: A payment workflow uses SQS and must preserve message order for each account while reducing duplicate processing attempts. Which queue type and message metadata should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a payment workflow uses SQS and must preserve message order for each account while reducing duplicate processing attempts. Which queue type and message metadata should the developer use.`
- Correct answer: an SQS FIFO queue with message group and deduplication IDs
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 19. Expected D, received F

- Rows: `229`; occurrences: `1`
- Question: A production Lambda function can overwhelm a downstream database during traffic spikes, but the team also wants guaranteed capacity for that function. Which Lambda setting should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a production Lambda function can overwhelm a downstream database during traffic spikes, but the team also wants guaranteed capacity for that function. Which Lambda setting should the developer configure.`
- Correct answer: Configure Lambda reserved concurrency
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 20. Expected D, received F

- Rows: `226`; occurrences: `1`
- Question: A public API must protect its backend from sudden request spikes by limiting client request rates. Which API Gateway feature should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a public API must protect its backend from sudden request spikes by limiting client request rates. Which API Gateway feature should the developer configure.`
- Correct answer: Configure API Gateway throttling
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 21. Expected D, received F

- Rows: `221`; occurrences: `1`
- Question: A serverless application has intermittent latency across several downstream calls. Which AWS service should the developer use to trace each request through the distributed workflow?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a serverless application has intermittent latency across several downstream calls. Which AWS service should the developer use to trace each request through the distributed workflow.`
- Correct answer: AWS X-Ray
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 22. Expected D, received F

- Rows: `228`; occurrences: `1`
- Question: A serverless maintenance task needs to invoke a Lambda function every hour. Which AWS service feature should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a serverless maintenance task needs to invoke a Lambda function every hour. Which AWS service feature should the developer configure.`
- Correct answer: an EventBridge scheduled rule
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 23. Expected D, received F

- Rows: `233`; occurrences: `1`
- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable.`
- Correct answer: Enable DynamoDB Time to Live
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 24. Expected D, received F

- Rows: `218`; occurrences: `1`
- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure.`
- Correct answer: an API Gateway Lambda authorizer
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 25. Expected F, received D

- Rows: `32`; occurrences: `1`
- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Expected rating: `0.25`
- User answer: `Which API Gateway feature should be used to run token validation on requests?`
- Correct answer: an API Gateway Lambda authorizer
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 26. Expected D, received F

- Rows: `243`; occurrences: `1`
- Question: A team releases a new Lambda version and wants 10 percent of alias traffic to move first, with automatic rollback if CloudWatch alarms fire. Which deployment service should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a team releases a new Lambda version and wants 10 percent of alias traffic to move first, with automatic rollback if CloudWatch alarms fire. Which deployment service should the developer use.`
- Correct answer: CodeDeploy for Lambda traffic shifting
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 27. Expected D, received F

- Rows: `238`; occurrences: `1`
- Question: A web application must let an authenticated user download one private S3 object for a limited time without changing the bucket to public access. What should the developer generate?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain a web application must let an authenticated user download one private S3 object for a limited time without changing the bucket to public access. What should the developer generate.`
- Correct answer: Generate an S3 presigned URL
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 28. Expected C, received D

- Rows: `31`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.75`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 29. Expected B, received D

- Rows: `27`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.85`
- User answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 30. Expected D, received F

- Rows: `237`; occurrences: `1`
- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure.`
- Correct answer: Configure SNS subscription filter policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 31. Expected D, received F

- Rows: `224`; occurrences: `1`
- Question: An SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message.`
- Correct answer: Adjust the SQS visibility timeout
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 32. Expected D, received F

- Rows: `225`; occurrences: `1`
- Question: An application must run code whenever items in a DynamoDB table are inserted, updated, or deleted. Which event-driven pattern should the developer configure?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an application must run code whenever items in a DynamoDB table are inserted, updated, or deleted. Which event-driven pattern should the developer configure.`
- Correct answer: DynamoDB Streams with Lambda
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 33. Expected D, received F

- Rows: `240`; occurrences: `1`
- Question: An application needs to encrypt large payloads locally while using AWS KMS to protect the key material. Which encryption pattern should the developer implement?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an application needs to encrypt large payloads locally while using AWS KMS to protect the key material. Which encryption pattern should the developer implement.`
- Correct answer: KMS envelope encryption
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 34. Expected D, received F

- Rows: `230`; occurrences: `1`
- Question: An asynchronously invoked Lambda function must send successful results to one target and failed invocation records to another target for follow-up processing. Which feature should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an asynchronously invoked Lambda function must send successful results to one target and failed invocation records to another target for follow-up processing. Which feature should the developer use.`
- Correct answer: Configure Lambda destinations
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 35. Expected D, received F

- Rows: `234`; occurrences: `1`
- Question: An order workflow must update an inventory item and create an order item in DynamoDB, and either both writes must succeed or neither should be saved. Which DynamoDB API pattern should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain an order workflow must update an inventory item and create an order item in DynamoDB, and either both writes must succeed or neither should be saved. Which DynamoDB API pattern should the developer use.`
- Correct answer: DynamoDB TransactWriteItems
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 36. Expected D, received F

- Rows: `71, 111, 151, 191`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to act as stateful virtual firewalls controlling inbound and outbound traffic for resources.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to act as stateful virtual firewalls controlling inbound and outbound traffic for resources.`
- Correct answer: VPC security groups
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 37. Expected D, received F

- Rows: `95, 135, 175, 215`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to add user sign-up, sign-in, and identity management to applications.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to add user sign-up, sign-in, and identity management to applications.`
- Correct answer: Amazon Cognito
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 38. Expected D, received F

- Rows: `67, 107, 147, 187`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.`
- Correct answer: Auto Scaling groups
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 39. Expected D, received F

- Rows: `61, 101, 141, 181`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.`
- Correct answer: S3 lifecycle policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 40. Expected D, received F

- Rows: `47`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.
- Expected rating: `0.65`
- User answer: `Use S3 bucket policies.`
- Correct answer: S3 lifecycle policies
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: S3 lifecycle policies is a better option because it is designed to automatically transition or expire objects based on age and access patterns, while S3 bucket policies does not satisfy that requirement.
- Reviewer feedback: Can you help me understand the difference between lifecycle policies and bucket policies?
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 41. Expected D, received F

- Rows: `69, 109, 149, 189`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to cache and deliver content from edge locations to reduce latency for users.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to cache and deliver content from edge locations to reduce latency for users.`
- Correct answer: Amazon CloudFront
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 42. Expected D, received F

- Rows: `94, 134, 174, 214`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to centralize and automate backup policies across supported AWS services.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to centralize and automate backup policies across supported AWS services.`
- Correct answer: AWS Backup
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 43. Expected D, received F

- Rows: `90, 130, 170, 210`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to centrally manage multiple AWS accounts and apply service control policies.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to centrally manage multiple AWS accounts and apply service control policies.`
- Correct answer: AWS Organizations
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 44. Expected D, received F

- Rows: `74, 114, 154, 194`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to collect metrics, logs, alarms, and dashboards for monitoring AWS resources.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to collect metrics, logs, alarms, and dashboards for monitoring AWS resources.`
- Correct answer: Amazon CloudWatch
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 45. Expected C, received F

- Rows: `38`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.75`
- User answer: `Encryption keys protect data in AWS services.`
- Correct answer: AWS KMS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Letter-grade verification answer: covers the security domain and key concepts but misses the AWS KMS service name, so it should receive C.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 46. Expected D, received F

- Rows: `76, 116, 156, 196`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.`
- Correct answer: AWS KMS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 47. Expected C, received F

- Rows: `51`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Expected rating: `0.75`
- User answer: `Use AWS Secrets Manager`
- Correct answer: AWS KMS
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: This exact service answer is not in the question's correct answer list.
- Reviewer feedback: When the best wrong answer is in the answer I think we should give the user a grade of either C or D depending on how wrong the answer is.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Runtime exact-service guard treated the answer as a wrong option before partial-credit semantics were considered.

### 48. Expected D, received F

- Rows: `84, 124, 164, 204`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to create point-in-time backups of block storage volumes for recovery or copying.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to create point-in-time backups of block storage volumes for recovery or copying.`
- Correct answer: Amazon EBS snapshots
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 49. Expected D, received F

- Rows: `82, 122, 162, 202`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to create, publish, secure, monitor, and throttle APIs for backend services.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to create, publish, secure, monitor, and throttle APIs for backend services.`
- Correct answer: Amazon API Gateway
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 50. Expected D, received F

- Rows: `78, 118, 158, 198`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to decouple application components with a managed message queue.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to decouple application components with a managed message queue.`
- Correct answer: Amazon SQS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 51. Expected D, received F

- Rows: `68, 108, 148, 188`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to distribute traffic across healthy targets to improve availability and scalability.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to distribute traffic across healthy targets to improve availability and scalability.`
- Correct answer: Elastic Load Balancing
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 52. Expected D, received F

- Rows: `79, 119, 159, 199`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to fan out messages to multiple subscribers using a managed pub/sub service.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to fan out messages to multiple subscribers using a managed pub/sub service.`
- Correct answer: Amazon SNS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 53. Expected D, received F

- Rows: `57, 97, 137, 177`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to grant temporary credentials to trusted AWS resources without storing long-term access keys.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to grant temporary credentials to trusted AWS resources without storing long-term access keys.`
- Correct answer: IAM roles
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 54. Expected D, received F

- Rows: `59, 99, 139, 179`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to improve high availability and fault tolerance during an Availability Zone impairment.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to improve high availability and fault tolerance during an Availability Zone impairment.`
- Correct answer: multiple Availability Zones
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 55. Expected A, received B

- Rows: `28`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.95`
- User answer: `AWS Kinesis`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `84.00`; runtime score: `84`
- Runtime feedback: Please write full sentence answers for full credit.
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Largest feature contributions: `semantic_similarity_score` +0.840
- Suspected cause: Conflicting curated labels: the same normalized question and answer has multiple expected grades.

### 56. Expected D, received F

- Rows: `89, 129, 169, 209`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.`
- Correct answer: Amazon Kinesis Data Streams
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 57. Expected D, received F

- Rows: `81, 121, 161, 201`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to orchestrate multi-step workflows and coordinate distributed application components.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to orchestrate multi-step workflows and coordinate distributed application components.`
- Correct answer: AWS Step Functions
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 58. Expected D, received F

- Rows: `87, 127, 167, 207`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to perform serverless data integration, cataloging, and ETL jobs.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to perform serverless data integration, cataloging, and ETL jobs.`
- Correct answer: AWS Glue
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 59. Expected D, received F

- Rows: `60, 100, 140, 180`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to preserve, retrieve, and restore previous versions of objects after overwrite or delete events.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to preserve, retrieve, and restore previous versions of objects after overwrite or delete events.`
- Correct answer: Amazon S3 versioning
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 60. Expected D, received F

- Rows: `96, 136, 176, 216`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to protect web applications from common web exploits using rules.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to protect web applications from common web exploits using rules.`
- Correct answer: AWS WAF
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 61. Expected D, received F

- Rows: `64, 104, 144, 184`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide a fully managed NoSQL key-value and document database with low-latency access.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide a fully managed NoSQL key-value and document database with low-latency access.`
- Correct answer: Amazon DynamoDB
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 62. Expected D, received F

- Rows: `92, 132, 172, 212`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide recommendations for cost optimization, security, fault tolerance, performance, and service limits.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide recommendations for cost optimization, security, fault tolerance, performance, and service limits.`
- Correct answer: AWS Trusted Advisor
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 63. Expected D, received F

- Rows: `70, 110, 150, 190`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.`
- Correct answer: Amazon Route 53
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 64. Expected D, received F

- Rows: `83, 123, 163, 203`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide shared elastic file storage that can be mounted by multiple compute resources.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide shared elastic file storage that can be mounted by multiple compute resources.`
- Correct answer: Amazon EFS
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 65. Expected D, received F

- Rows: `72, 112, 152, 192`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.`
- Correct answer: network ACLs
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 66. Expected D, received F

- Rows: `62, 102, 142, 182`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to provide synchronous standby replication and automatic failover for relational databases.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to provide synchronous standby replication and automatic failover for relational databases.`
- Correct answer: Amazon RDS Multi-AZ
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 67. Expected D, received F

- Rows: `50`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to provide synchronous standby replication and automatic failover for relational databases.
- Expected rating: `0.65`
- User answer: `Use read replica only.`
- Correct answer: Amazon RDS Multi-AZ
- Raw model score: `49.00`; runtime score: `49`
- Runtime feedback: Amazon RDS Multi-AZ is a better option because it is designed to provide synchronous standby replication and automatic failover for relational databases, while read replica only does not satisfy that requirement.
- Largest feature contributions: `semantic_similarity_score` +0.490
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 68. Expected D, received F

- Rows: `88, 128, 168, 208`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to query data in Amazon S3 using SQL without managing servers.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to query data in Amazon S3 using SQL without managing servers.`
- Correct answer: Amazon Athena
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 69. Expected D, received F

- Rows: `73, 113, 153, 193`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.`
- Correct answer: AWS CloudTrail
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 70. Expected D, received F

- Rows: `65, 105, 145, 185`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.`
- Correct answer: DynamoDB global tables
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 71. Expected D, received F

- Rows: `93, 133, 173, 213`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to review workloads against AWS best practices and identify improvement opportunities.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to review workloads against AWS best practices and identify improvement opportunities.`
- Correct answer: AWS Well-Architected Tool
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 72. Expected D, received F

- Rows: `80, 120, 160, 200`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.`
- Correct answer: Amazon EventBridge
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 73. Expected D, received F

- Rows: `5`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Expected rating: `0.65`
- User answer: `route 53`
- Correct answer: Amazon EventBridge
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 74. Expected D, received F

- Rows: `86, 126, 166, 206`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to run analytical queries against a managed petabyte-scale data warehouse.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to run analytical queries against a managed petabyte-scale data warehouse.`
- Correct answer: Amazon Redshift
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 75. Expected D, received F

- Rows: `66, 106, 146, 186`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to run event-driven code without managing servers and scale per request.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to run event-driven code without managing servers and scale per request.`
- Correct answer: AWS Lambda
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 76. Expected D, received F

- Rows: `63, 103, 143, 183`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to scale read-heavy database workloads by serving read traffic from replicated database instances.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to scale read-heavy database workloads by serving read traffic from replicated database instances.`
- Correct answer: Amazon RDS read replicas
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 77. Expected D, received F

- Rows: `91, 131, 171, 211`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to set maximum available permissions across accounts in an AWS Organization.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to set maximum available permissions across accounts in an AWS Organization.`
- Correct answer: Service Control Policies
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 78. Expected D, received F

- Rows: `85, 125, 165, 205`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to store rarely accessed archival data at lower cost with retrieval-time tradeoffs.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to store rarely accessed archival data at lower cost with retrieval-time tradeoffs.`
- Correct answer: S3 Glacier storage classes
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 79. Expected D, received F

- Rows: `2`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.65`
- User answer: `AWS Key Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 80. Expected C, received D

- Rows: `13`; occurrences: `1`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.75`
- User answer: `Parameter Store`
- Correct answer: AWS Secrets Manager
- Raw model score: `65.00`; runtime score: `65`
- Runtime feedback: 
- Largest feature contributions: `semantic_similarity_score` +0.650
- Suspected cause: The expected grade and model score disagree; inspect the curated label and feature calibration together.

### 81. Expected D, received F

- Rows: `77, 117, 157, 197`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.`
- Correct answer: AWS Secrets Manager
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 82. Expected D, received F

- Rows: `58, 98, 138, 178`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.`
- Correct answer: AWS Budgets
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 83. Expected D, received F

- Rows: `75, 115, 155, 195`; occurrences: `4`
- Question: Explain which AWS service or feature should be used to track resource configuration history and evaluate compliance against rules.
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain which AWS service or feature should be used to track resource configuration history and evaluate compliance against rules.`
- Correct answer: AWS Config
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 84. Expected D, received F

- Rows: `249`; occurrences: `1`
- Question: Multiple Lambda functions use the same internal utility library, and the team wants to manage that library separately from each function package. Which Lambda feature should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain multiple Lambda functions use the same internal utility library, and the team wants to manage that library separately from each function package. Which Lambda feature should the developer use.`
- Correct answer: a Lambda layer
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 85. Expected D, received F

- Rows: `251`; occurrences: `1`
- Question: Review the IAM policy for the Lambda execution role. What is the access-control issue, and what change best matches least privilege?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain review the IAM policy for the Lambda execution role. What is the access-control issue, and what change best matches least privilege.`
- Correct answer: Restrict the Resource to arn:aws:s3:::example-bucket/reports/*
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 86. Expected D, received F

- Rows: `252`; occurrences: `1`
- Question: Review the Lambda handler. What security problem should the developer fix before deployment, and what AWS service is the best fit?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain review the Lambda handler. What security problem should the developer fix before deployment, and what AWS service is the best fit.`
- Correct answer: Store the credential in AWS Secrets Manager and retrieve it at runtime
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 87. Expected D, received F

- Rows: `254`; occurrences: `1`
- Question: Review the SAM template. The function deploys but receives AccessDenied when it calls GetItem. What is missing from the template?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain review the SAM template. The function deploys but receives AccessDenied when it calls GetItem. What is missing from the template.`
- Correct answer: Add a least-privilege DynamoDB read policy for the Sessions table to the function
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 88. Expected D, received F

- Rows: `253`; occurrences: `1`
- Question: Review the SDK helper. Why can this function miss objects, and what SDK pattern should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain review the SDK helper. Why can this function miss objects, and what SDK pattern should the developer use.`
- Correct answer: an S3 ListObjectsV2 paginator and iterate through every page
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 89. Expected D, received F

- Rows: `241`; occurrences: `1`
- Question: Several Lambda functions need to read shared non-rotating configuration values organized by application and environment path. Which AWS service should the developer use?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain several Lambda functions need to read shared non-rotating configuration values organized by application and environment path. Which AWS service should the developer use.`
- Correct answer: Systems Manager Parameter Store
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 90. Expected D, received F

- Rows: `247`; occurrences: `1`
- Question: Several services publish domain events, and the platform team wants rules to route matching custom events to different Lambda targets without direct service-to-service calls. Which EventBridge resource should be used?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain several services publish domain events, and the platform team wants rules to route matching custom events to different Lambda targets without direct service-to-service calls. Which EventBridge resource should be used.`
- Correct answer: a custom EventBridge event bus with rules
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

### 91. Expected D, received F

- Rows: `219`; occurrences: `1`
- Question: Two application instances may try to create the same DynamoDB item at the same time. Which DynamoDB write approach should the developer use to prevent replacing an existing item?
- Expected rating: `0.65`
- User answer: `This question is asking the learner to identify and explain two application instances may try to create the same DynamoDB item at the same time. Which DynamoDB write approach should the developer use to prevent replacing an existing item.`
- Correct answer: a DynamoDB conditional write
- Raw model score: `25.00`; runtime score: `25`
- Runtime feedback: This answer restates the question without identifying and explaining the solution.
- Reviewer feedback: Generated question-restatement negative example: this answer rewords the prompt without identifying the correct AWS service, feature, or reasoning.
- Largest feature contributions: `semantic_similarity_score` +0.250
- Suspected cause: Sparse alias or partial-concept answer has low lexical overlap with the long reference answer. The feature set lacks service aliases and calibrated partial-credit semantics.

## Recommended Remediation Order

1. Reconcile conflicting curated labels before changing model code.
2. Expand normalized AWS service aliases and near-service synonym handling.
3. Tune concept-coverage thresholds against curated examples.
4. Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.

