# Curated Rubric Review

- Curated examples reviewed: 300
- Rubric grades: `A`, `B`, `C`, `D`, `F`
- Current grade distribution: `{'A': 21, 'B': 20, 'C': 21, 'D': 218, 'F': 20}`
- Suggested label updates: 28

## Suggested Answer Updates

### Row 6: B -> A

- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Answer: `CloudTrail records AWS API activity.`
- Reference: AWS CloudTrail
- Semantic score: `90`
- Reviewer feedback: Balanced grade example: correct service and basic purpose, but limited explanation.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 10: B -> C

- Question: A Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime?
- Answer: `Environment variables.`
- Reference: Lambda environment variables
- Semantic score: `75`
- Reviewer feedback: Balanced grade example: names the intended feature but does not explain the Lambda or non-secret constraint.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 12: B -> C

- Question: A serverless maintenance task needs to invoke a Lambda function every hour. Which AWS service feature should the developer configure?
- Answer: `EventBridge schedule.`
- Reference: an EventBridge scheduled rule
- Semantic score: `75`
- Reviewer feedback: Balanced grade example: correct feature name with minimal reasoning.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 13: C -> F

- Question: Explain which AWS service or feature should be used to decouple application components with a managed message queue.
- Answer: `Use Amazon SNS because it sends messages between parts of an application.`
- Reference: Amazon SQS
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: recognizes messaging but selects publish-subscribe instead of a queue.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 14: C -> F

- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Answer: `Use CloudWatch Logs for operational logs and troubleshooting.`
- Reference: AWS CloudTrail
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: adjacent observability service but misses API activity audit history.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 15: C -> D

- Question: Explain which AWS service or feature should be used to automatically transition or expire objects based on age and access patterns.
- Answer: `Use S3 storage classes to move older objects to cheaper tiers.`
- Reference: S3 lifecycle policies
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: identifies the storage-class domain but omits Lifecycle rules and expiration.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 16: C -> D

- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Answer: `Use RDS read replicas for low-latency reads in another location.`
- Reference: DynamoDB global tables
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: understands read replication but chooses the wrong database boundary.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 17: C -> D

- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Answer: `Use Systems Manager Parameter Store to keep configuration values out of code.`
- Reference: AWS Secrets Manager
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: related configuration storage, but misses the scheduled secret rotation requirement.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 18: C -> F

- Question: A Lambda function needs different non-secret configuration values in development and production. Which Lambda feature should the developer use to pass those values at runtime?
- Answer: `Use AWS Systems Manager Parameter Store for application settings.`
- Reference: Lambda environment variables
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: related configuration service, but not the direct Lambda runtime feature requested.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 19: C -> D

- Question: A public API must protect its backend from sudden request spikes by limiting client request rates. Which API Gateway feature should the developer configure?
- Answer: `Configure a CloudWatch alarm when request counts are high.`
- Reference: Configure API Gateway throttling
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: recognizes traffic monitoring but does not enforce client request limits.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 20: C -> D

- Question: A serverless maintenance task needs to invoke a Lambda function every hour. Which AWS service feature should the developer configure?
- Answer: `Use an SQS delay queue to run the task later.`
- Reference: an EventBridge scheduled rule
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: related asynchronous timing concept, but not recurring scheduling.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 21: C -> F

- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Answer: `Use S3 lifecycle rules to expire old objects.`
- Reference: Enable DynamoDB Time to Live
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: recognizes lifecycle expiration, but applies the S3 feature instead of DynamoDB TTL.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 22: C -> F

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `Use separate SQS queues for each order type.`
- Reference: Configure SNS subscription filter policies
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: understands subscriber separation but misses SNS message attribute filtering.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 35: C -> F

- Question: Explain which AWS service or feature should be used to cache and deliver content from edge locations to reduce latency for users.
- Answer: `Use Route 53 because it routes users to endpoints.`
- Reference: Amazon CloudFront
- Semantic score: `25`
- Reviewer feedback: Balanced grade example: related edge/networking idea, but misses CDN caching.
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 36: C -> D

- Question: Explain which AWS service or feature should be used to run event-driven code without managing servers and scale per request.
- Answer: `Use AWS Fargate for serverless container compute.`
- Reference: AWS Lambda
- Semantic score: `65`
- Reviewer feedback: Balanced grade example: recognizes managed compute but misses the event-driven Lambda service boundary.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 45: D -> F

- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Answer: `AWS Key Store`
- Reference: AWS Secrets Manager
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 47: B -> C

- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Answer: `AWS Kinesis`
- Reference: Amazon Kinesis Data Streams
- Semantic score: `75`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 48: D -> F

- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Answer: `route 53`
- Reference: Amazon EventBridge
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 68: A -> B

- Question: A deployment workflow uses a managed build project that must run the same install, build, and test commands every time. Where should the developer define those command phases?
- Answer: `AWS Code Build`
- Reference: a CodeBuild buildspec file
- Semantic score: `85`
- Reviewer feedback: Again my answer is correct. Are you sure you are using the semantic evaluation logic?
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 70: B -> D

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know. `
- Reference: Configure SNS subscription filter policies
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 71: A -> C

- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Answer: `AWS Kinesis`
- Reference: Amazon Kinesis Data Streams
- Semantic score: `75`
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 74: C -> D

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know. `
- Reference: Configure SNS subscription filter policies
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 75: F -> D

- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Answer: `Which API Gateway feature should be used to run token validation on requests? `
- Reference: an API Gateway Lambda authorizer
- Semantic score: `65`
- Rationale: The answer names an adjacent AWS concept, so the standardized rubric gives minimal partial credit instead of no credit.

### Row 87: C -> D

- Question: Explain which AWS service or feature should be used to act as stateful virtual firewalls controlling inbound and outbound traffic for resources.
- Answer: `AWF Shield or AWS Groups can be used as a stateful firewall to control inbound and outbound traffic. `
- Reference: VPC security groups
- Semantic score: `65`
- Reviewer feedback: Correct answer was present but initial answer was definitely wrong.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 95: C -> D

- Question: Review the SDK helper. Why can this function miss objects, and what SDK pattern should the developer use?
- Answer: `The bucket contains more objects than a single ListObjectsV2 response can return.
`
- Reference: an S3 ListObjectsV2 paginator and iterate through every page
- Semantic score: `65`
- Reviewer feedback: -- I think you gave away the answer in the question.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 99: A -> D

- Question: Explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.
- Answer: `Vertical scaling involves making the individual instances of the EC2 instance bigger while horizontal scaling makes more instances. `
- Reference: Auto Scaling groups
- Semantic score: `65`
- Reviewer feedback: We need to add a question about vertical scaling.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 298: A -> D

- Question: Review the IAM policy for the Lambda execution role. What is the access-control issue, and what change best matches least privilege?
- Answer: `Change resource to 
"Resource": "s3://example-bucket/reports/*"`
- Reference: Restrict the Resource to arn:aws:s3:::example-bucket/reports/*
- Semantic score: `65`
- Reviewer feedback: My answer exactly matches the proposed code block.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 299: C -> D

- Question: Explain which AWS service or feature should be used to adjust EC2 capacity automatically based on demand and health checks.
- Answer: `Elastic load balancing is a way of automatically adjusting demand based on health checks. `
- Reference: Auto Scaling groups
- Semantic score: `65`
- Reviewer feedback: Elastic Load balancing is a sub feature of auto scaling groups
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

## Release Table Recommendation

Keep `Release`, `Semantic Accuracy`, `Semantic Precision`, `Semantic Recall`, `Exact Letter Accuracy`, and `Question Fidelity` in release notes.
Calculate `Semantic Accuracy` as grade-band agreement and `Exact Letter Accuracy` as strict A/B/C/D/F agreement on curated answer rows.
Use the semantic benchmark as the single answer-scoring release metric source.

