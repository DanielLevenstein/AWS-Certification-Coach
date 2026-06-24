# AWS Certification Coach TODO

The previous TODO was backed up to `docs/TODO_COPY.md` before this roadmap was created.

## Release Discipline

- Run `./clean.sh` before regenerating artifacts when schema or generated-data behavior changes.
- Run `./setup.sh` after cleaning to regenerate local test data.
- Run `./run_unit_tests.sh` before considering a milestone ready.
- Run release metrics before any commit that claims a release milestone.
- Update `docs/RELEASE_NOTES.md` for each release with a one-line change description and release metrics.
- Do not commit `data/`, `scripts/data/`, or `metrics/`.
- Do not push Docker images or create GitHub tags until a human reviews the changes.

# Phase 1 Planning and Rubric Stabilization
## Rubric Stabilization
Done
## Answer Grading Stabilization
Done
## Answer Rubric Data Contract
Done
## Model Stabilization
In Progress: 
The current model struggles with minor rewordings of answers which probably will some significant redesign. 
Because the current accuracy metrics are stable, we are implementing these changes on a fresh feature branch to ensure the production app remains stable.

Implementing dedicated AWS knowledge based on a dedicated feature branch using tinyLLama for local training.
My hope is to get the local language model to train the existing classifier to improve its accuracy scores so a heavy language model doesn't have to get deployed to production.  

1) Update model tests to separate training and smoke testing. 
2) Add a playwrite test to the deployment guardrail which tests that the first question of the test displays and then move the deployment test into its own test suite per our test suite design. 
3) Release metrics from train_accuracy_model.sh and release_notes.sh don't match. We need to determine which metrics should be used. We are currently using the values from the release_notes.sh script.

| Release                 |      A |      B |      C |       D |      F |
|:------------------------|-------:|-------:|-------:|--------:|-------:|
| release_notes.sh        | 50.00% | 70.59% | 50.00% | 100.00% | 85.71% |
| train_accuracy_model.sh | 42.42% | 66.67% | 34.78% | 77.78% | 100.00% |

Update release guardrail to use the exact letter match as its release metric once we get the metric above the satisfactory value.
This will allow us to deprecate the old metrics completely.


# Phase 2 Code & Configuration Review
IAM policy questions.
Lambda code questions.
SDK usage questions.
CloudFormation/SAM questions.
API Gateway configuration questions.
DynamoDB query examples.
CI/CD configuration scenarios.
Log analysis and troubleshooting.

# Phase 3: Tradeoff Analysis
Service comparisons.
Architecture reasoning.
Solution selection.
Cost/scalability discussions.

# Phase 4: Advanced Feedback
Concept tracking.
Learning analytics.
Weakness detection.
Personalized recommendations


## Backlog

- Decide whether app navigation should expose question type filters.
- Decide whether multiple-choice source provenance should be collapsible, sidebar-only, or shown after answer submission.
- Add authoring guidance for self-authored AWS-valid and exam-valid source rows.
- Add a human-review checklist for generated question batches.
- Expand Developer Associate source coverage beyond serverless, messaging, deployment, and data-access patterns.
