# Curated Rubric Review

- Curated examples reviewed: 109
- Rubric grades: `A`, `B`, `C`, `D`, `F`
- Current grade distribution: `{'A': 20, 'B': 16, 'C': 12, 'D': 36, 'F': 25}`
- Suggested label updates: 9

## Suggested Answer Updates

### Row 50: D -> F

- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Answer: `AWS Key Store`
- Reference: AWS Secrets Manager
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 52: B -> C

- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Answer: `AWS Kinesis`
- Reference: Amazon Kinesis Data Streams
- Semantic score: `75`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 53: D -> F

- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Answer: `route 53`
- Reference: Amazon EventBridge
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 66: D -> A

- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Answer: `Which API Gateway feature should be used to run token validation on requests? `
- Reference: an API Gateway Lambda authorizer
- Semantic score: `95`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 73: B -> D

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know. `
- Reference: Configure SNS subscription filter policies
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 74: A -> C

- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Answer: `AWS Kinesis`
- Reference: Amazon Kinesis Data Streams
- Semantic score: `75`
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 75: C -> D

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know. `
- Reference: Configure SNS subscription filter policies
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 76: F -> A

- Question: A team exposes a Lambda-backed REST API and must run custom token validation before requests reach the backend function. Which API Gateway feature should the developer configure?
- Answer: `Which API Gateway feature should be used to run token validation on requests? `
- Reference: an API Gateway Lambda authorizer
- Semantic score: `95`
- Rationale: The answer names an adjacent AWS concept, so the standardized rubric gives minimal partial credit instead of no credit.

### Row 85: C -> D

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

