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


# New Accuracy Metrics
| Release | Curated grade-band accuracy | Generated-label MSE | Generated-label MAE | 
|---------|----------------------------:|--------------------:|--------------------:|
| v1.3.1  |                      44.00% |              0.0107 |              0.0761 |  
| v1.3.2  |                      68.00% |              0.0027 |              0.0362 |   
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
