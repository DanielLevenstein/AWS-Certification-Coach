# Curated Rubric Review

- Curated examples reviewed: 24
- Rubric grades: `A`, `B`, `C`, `D`, `F`
- Current grade distribution: `{'A': 4, 'B': 3, 'C': 4, 'D': 6, 'F': 7}`
- Suggested label updates: 10

## Suggested Answer Updates

### Row 9: B -> F

- Question: Explain which AWS service or feature should be used to track cost or usage thresholds and send alerts for actual or forecasted spending.
- Answer: `AWS Cost Center`
- Reference: AWS Budgets
- Semantic score: `25`
- Rationale: The answer does not identify the required service or enough relevant AWS reasoning for partial credit.

### Row 10: C -> D

- Question: Explain which AWS service or feature should be used to provide scalable DNS routing and health-check-based routing for applications.
- Answer: `route 55`
- Reference: Amazon Route 53
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 11: C -> D

- Question: Explain which AWS service or feature should be used to provide stateless subnet-level traffic filtering with explicit inbound and outbound rules.
- Answer: `Allow and deny rules`
- Reference: network ACLs
- Semantic score: `62`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 13: F -> D

- Question: Explain which AWS service or feature should be used to store, retrieve, and rotate application secrets such as database credentials.
- Answer: `Parameter Store`
- Reference: AWS Secrets Manager
- Semantic score: `65`
- Rationale: The answer names an adjacent AWS concept, so the standardized rubric gives minimal partial credit instead of no credit.

### Row 16: A -> B

- Question: Explain which AWS service or feature should be used to create and manage encryption keys used to protect data in AWS services.
- Answer: `AWS KMS`
- Reference: AWS KMS
- Semantic score: `84`
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

### Row 21: C -> D

- Question: A developer must keep application database passwords out of code and periodically replace them without a manual handoff. Which AWS service should manage this credential lifecycle?
- Answer: `AWS KMS Keys`
- Reference: AWS Secrets Manager
- Semantic score: `65`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 22: C -> D

- Question: Explain which AWS service or feature should be used to replicate tables across Regions for low-latency multi-Region access and resilience.
- Answer: `RDS read replicas can be used for low-latency data synchronization across multiple availability zones.`
- Reference: DynamoDB global tables
- Semantic score: `62`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

### Row 23: A -> C

- Question: Explain which AWS service or feature should be used to record AWS API activity for auditing, governance, and operational troubleshooting.
- Answer: `AWS Cloud trail is used to record AWS API activity for auditing. `
- Reference: AWS CloudTrail
- Semantic score: `72`
- Rationale: The current label and scorer disagree on the standardized exact letter grade; review this as a calibration candidate.

## Release Table Recommendation

Keep `Release`, `Semantic Accuracy`, `Semantic Precision`, `Semantic Recall`, and `Question Fidelity` in release notes.
Calculate `Semantic Accuracy` as exact A/B/C/D/F letter-grade agreement on curated answer rows.
Do not publish `Training Accuracy` or `Saved Accuracy`; keep those values in generated JSON artifacts only for model-training diagnostics.

