# Curated Rubric Review

- Curated examples reviewed: 37
- Rubric grades: `A`, `B`, `C`, `D`, `F`
- Current grade distribution: `{'A': 9, 'B': 5, 'C': 4, 'D': 9, 'F': 10}`
- Suggested label updates: 11

## Suggested Answer Updates

### Row 2: D -> F

- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Answer: `AWS Key Store`
- Reference: AWS Secrets Manager
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 5: A -> F

- Question: Explain which AWS service or feature should be used to route events from AWS services and applications to targets using event buses and rules.
- Answer: `route 53`
- Reference: Amazon EventBridge
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 11: C -> D

- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Answer: `Allow and deny rules`
- Reference: network ACLs
- Semantic score: `62`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 16: B -> A

- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Answer: `AWS KMS`
- Reference: AWS KMS
- Semantic score: `95`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 17: A -> B

- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Answer: `AWS KMS creates and manages encryption keys that protect data.`
- Reference: AWS KMS
- Semantic score: `88`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 18: A -> B

- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Answer: `AWS KMS manages encryption keys.`
- Reference: AWS KMS
- Semantic score: `88`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 25: A -> B

- Question: A session table in DynamoDB stores an expiration time for each item and should remove old sessions without a scheduled cleanup job. Which feature should the developer enable?
- Answer: `DynamoDB Time to Live can be used to remove old DynamoDB sections with a scheduled cleanup job. `
- Reference: Enable DynamoDB Time to Live
- Semantic score: `84`
- Reviewer feedback: This is a full answer it's just worded slightly differently
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 27: C -> B

- Question: An SQS consumer sometimes needs several minutes to finish processing a message. Which queue setting should the developer adjust so another worker does not immediately receive the same message?
- Answer: `SQS FILO queue`
- Reference: Adjust the SQS visibility timeout
- Semantic score: `84`
- Reviewer feedback: My answer had nothing to do with the cannon answer but might still be partially right.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 29: A -> B

- Question: Explain which AWS service or feature should be used to ingest and process real-time streaming data at scale.
- Answer: `AWS Kinesis`
- Reference: Amazon Kinesis Data Streams
- Semantic score: `80`
- Reviewer feedback: This is a question which had been misguided for awhile so I think we need to add a it to our synonym list if we don't already have one.
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 32: C -> B

- Question: An SNS topic publishes all order events, but each subscribed queue should receive only messages for selected order types based on attributes. Which SNS feature should the developer configure?
- Answer: `SNS topics allow multiple receivers to see the same queue but I don't think it allows filtering based on attributes,  so I am going to have to go with I don't know. `
- Reference: Configure SNS subscription filter policies
- Semantic score: `84`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 35: C -> D

- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Answer: `RDS read replicas can be used for low-latency data synchronization across multiple availability zones.`
- Reference: DynamoDB global tables
- Semantic score: `62`
- Reviewer feedback: We need to decide in our design rubric if we are giving partial credit answers a score of Grade D or Grade C
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

## Release Table Recommendation

Keep `Release`, `Semantic Accuracy`, `Semantic Precision`, `Semantic Recall`, `Exact Letter Accuracy`, and `Question Fidelity` in release notes.
Calculate `Semantic Accuracy` as grade-band agreement and `Exact Letter Accuracy` as strict A/B/C/D/F agreement on curated answer rows.
Do not publish `Training Accuracy` or `Saved Accuracy`; keep those values in generated JSON artifacts only for model-training diagnostics.

