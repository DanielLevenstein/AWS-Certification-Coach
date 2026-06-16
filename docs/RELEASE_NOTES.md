# Release Notes

| Release | Description                                                                                                    |
|:--------|:---------------------------------------------------------------------------------------------------------------|
| v1.0.0  | Initial Streamlit/Docker release with generated AWS certification practice questions.                          |
| v1.1.0  | Expands the question bank to 80 AWS-docs-grounded questions, and adds stricter wrong-service answer rejection. |
| v1.1.2  | Changed rating to grade and added feedback system.                                                             |
| v1.1.3  | Gate feedback behind SHOW_FEEDBACK environmental variable.                                                     |
| v1.3.4  | Swaps app scoring from trained regression to semantic-aware grading.                                           |
| v1.4.0  | v1.4.0 Cleaning up schema                                                                                      |
| v1.4.1  | Accuracy went down after switching to long form answer format                                                  |
| v1.4.3  | Include both long and short form answers in training data                                                      |
| v1.4.4  | Switch back to long form answers in training data                                                              |
| Next    | Updated accuracy release script to ensure consistent metrics                                                   |
### Model Performance

# New Accuracy Metrics
| Release | Accuracy | Precision | Recall |
|---------|---------:|----------:|-------:|
| v1.3.1  |   44.00% |       TBD |    TBD |
| v1.3.2  |   68.00% |       TBD |    TBD |
| v1.3.3  |   68.00% |       TBD |    TBD |
| v1.3.4  |   80.00% |    87.50% | 87.50% |
| v1.4.1  |   68.00% |    87.50% | 87.50% |
| v1.4.2  |   76.00% |    84.62% | 68.75% |
| v1.4.3  |   76.00% |    84.62% | 68.75% |
| v1.4.4  |   68.00% |    84.62% | 68.75% |


| Release     | Semantic Accuracy | Training Accuracy | Semantic Diagnostic accuracy | Semantic Precision | Semantic Recall |
|-------------|------------------:|------------------:|-----------------------------:|-------------------:|----------------:|
| v1.5 Schema |            96.00% |            68.00% |                       68.00% |             84.62% |          68.75% |

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
