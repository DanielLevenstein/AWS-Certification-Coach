# Release Notes

- 4-digit release number is weight and documentation update only, or trivial UI changes.

| Release | Description                                                                                                       |
|:--------|:------------------------------------------------------------------------------------------------------------------|
| v1.0.0  | Initial Streamlit/Docker release with generated AWS certification practice questions.                             |
| v1.1.0  | Expands the question bank to 80 AWS-docs-grounded questions, and adds stricter wrong-service answer rejection.    |
| v1.1.2  | Changed rating to grade and added feedback system.                                                                |
| v1.1.3  | Gate feedback behind SHOW_FEEDBACK environmental variable.                                                        |
| v1.3.0   | Configured application to use the partial answer classifier instead of the binary classification model.  |
## v1.0.0 Release Details

### Model Performance


| Release | Accuracy | Precision | Recall | Full Examples | MSE    | MAE    | Partial Examples | TP  | FP | TN  | FN |
|---------|----------|-----------|--------|---------------|--------|--------|------------------|-----|----|-----|----| 
| v1.0.0  | 97.39%   | 97.19%    | 97.83% | 1150          | 0.0193 | 0.1006 | 500              | 587 | 17 | 533 | 13 |

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
