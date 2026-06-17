# Release Notes

| Release | Description                                                                                                    |
|:--------|:---------------------------------------------------------------------------------------------------------------|
| v1.0.0  | Initial Streamlit/Docker release with generated AWS certification practice questions.                          |
| v1.1.0  | Expands the question bank to 80 AWS-docs-grounded questions, and adds stricter wrong-service answer rejection. |
| v1.1.2  | Changed rating to grade and added feedback system.                                                             |
| v1.1.3  | Gate feedback behind SHOW_FEEDBACK environmental variable.                                                     |
| v1.3.4  | Swaps app scoring from trained regression to `semantic_similarity`.                                            |
| v1.4.0  | v1.4.0 Cleaning up schema                                                                                      |
| v1.4.1  | Accuracy went down after switching to long form answer format                                                  |
| v1.4.3  | Include both long and short form answers in training data                                                      |
| v1.4.4  | Switch back to long form answers in training data                                                              |
| v1.5.0  | Updated accuracy release script to ensure consistent metrics                                                   |
| v1.5.1  | Fix output of semantic metric chart, and move release metrics to folder with timestamps saved.                 |
| v1.5.3 | Updated test data to have proper train, test, validation split                                                 |
| v1.5.4 | Made `semantic_similarity` the official model name, moved release gating to 80% semantic precision.            |
| v1.5.5 | Created automated deployment script |


# Release Metrics

| Release | Saved Accuracy | Training Accuracy | Semantic Accuracy | Semantic Precision | Semantic Recall |
|:--------|---------------:|------------------:|------------------:|-------------------:|----------------:|
| v1.5.0  |         96.00% |            68.00% |            68.00% |             84.62% |          68.75% |
| v1.5.0  |         96.00% |            68.00% |            68.00% |             84.62% |          68.75% |
| v1.5.3 | 96.00% | 68.00% | 68.00% | 84.62% | 68.75% |
| v1.5.4 | 96.00% | 68.00% | 68.00% | 84.62% | 68.75% |
### Scope

Certifications:

- Cloud Practitioner
- Solutions Architect Associate

Difficulty:

- Easy
- Medium

<!-- release-metrics:start -->
# Latest Release Metrics

| Release | Saved Model Accuracy | Training Accuracy | Semantic Accuracy | Semantic Precision | Semantic Recall |
|:--------|---------------------:|------------------:|------------------:|-------------------:|----------------:|
| v1.5.4 | 96.00% | 68.00% | 68.00% | 84.62% | 68.75% |

Saved model answer form: `long`
Saved model calibration count: `18`

Training curve: `training_performance.png`
Curated grade-band accuracy (A/B, C/D, F): `curated_grade_accuracy.png`
`semantic_similarity` diagnostic chart: `semantic_accuracy.png`
Curated failure analysis: `curated_failure_report.md`

Semantic precision is the release guardrail for the `semantic_similarity` model.
Precision and recall treat A/B and C/D as accepted answers and F as rejected.
<!-- release-metrics:end -->
