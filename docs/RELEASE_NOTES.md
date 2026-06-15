# Release Notes

- 4-digit release number is weight and documentation update only, or trivial UI changes.


| Release  | Description                                                                                              |
|----------|----------------------------------------------------------------------------------------------------------|
| v1.0.0   | Initial Streamlit/Docker release with generated AWS certification practice questions                     |
|          | trained answer classifier, and partial-credit regression metrics.                                        |                                                                                    |
| v1.1.0   | Separates the app-facing question bank from training labels                                              | 
|          | expands the app bank to 80 AWS-docs-grounded questions and adds stricter wrong-service answer rejection. |
| v1.1.2   | Changed rating to grade and added feedback system                                                        |
| v1.1.2.1 | 1 failing test from curated training data: AWS Glacier                                                   |
| v1.1.3   | Added feedback package to source control and switched UI to show original question with answers hidden.  |
| v1.1.3.1 | Removed duplicate question from right side panel.                                                        |
| v1.3.0   | Configured application to use the partial answer classifier instead of the binary classification model.  |
| v1.3.1 | Test Case Redesign base accuracy 44% |

### Model Performance

| Release | Accuracy | Precision | Recall | Full Examples | MSE    | MAE    | Partial Examples | TP  | FP | TN  | FN |
|---------|----------|-----------|--------|---------------|--------|--------|------------------|-----|----|-----|----|
| v1.0.0  | 97.39%   | 97.19%    | 97.83% | 1150          | 0.0193 | 0.1006 | 500              | 587 | 17 | 533 | 13 |
| v1.1.2  | 99.01%   | 99.71%    | 98.44% | 1314          | 0.0099 | 0.0714 | 1314             | 694 | 2  | 607 | 11 |
| v1.3.0  | 99.01%   | 99.71%    | 98.44% | 1314          | 0.0105 | 0.0729 | 1321             | 694 | 2  | 607 | 11 |

# New Accuracy Metrics
| Curated grade-band accuracy | Generated-label MSE | Semantic-aware grading | Generated-label MAE | Unit coverage | Average complexity | Maximum complexity |
|----------------------------:|-------------------:|------------------------|-------------------:|--------------:|-------------------:|-------------------:|
|                      44.00% |             0.0107 | TBD                    |             0.0761 |        42.41% |               2.97 |                 11 |
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
