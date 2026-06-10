# Release Notes

| Release | Description                                                                                                                                                            |
|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| v1.1.0  | Separates the app-facing question bank from training labels, expands the app bank to 80 AWS-docs-grounded questions, and adds stricter wrong-service answer rejection. |
| v1.0.0  | Initial Streamlit/Docker release with generated AWS certification practice questions, trained answer classifier, and partial-credit regression metrics.                |

## v1.0.0 Release Details

### Model Performance

| Release | Accuracy | Precision | Recall | Full Answer Examples | Full Evaluation Mode   | MSE    | MAE    | Partial Examples | Partial Evaluation Mode | TP  | FP | TN  | FN |
|---------|----------|-----------|--------|----------------------|------------------------|--------|--------|------------------|-------------------------|-----|----|-----|----|
| v1.0.0  | 97.39%   | 97.19%    | 97.83% | 1150                 | leave-one-question-out | 0.0193 | 0.1006 | 500              | leave-one-question-out  | 587 | 17 | 533 | 13 |
| v1.1.0  | 97.39%   | 97.19%    | 97.83% | 1150                 | 0.0193                 | 0.1006 | 500    | 587              | 17                      | 533 | 13 |

### Scope

Certifications:

- Cloud Practitioner
- Solutions Architect Associate

Domains:

- Analytics
- Application Integration
- Billing
- Compute
- Database
- Governance
- Integration
- Networking
- Operations
- Resilient Architectures
- Security
- Storage

Difficulty:

- Easy
- Medium