# AWS Certification Coach TODO

The previous TODO was backed up to `docs/TODO_COPY.md` before this roadmap was created.

## Release Discipline

- Run `./clean.sh` before regenerating artifacts when schema or generated-data behavior changes.
- Run `./setup.sh` after cleaning to regenerate local test data.
- Run `./run_unit_tests.sh` before considering a milestone ready.
- Run release metrics before any commit that claims a release milestone.
- Update `RELEASE_NOTES.md` for each release with a one-line change description and release metrics.
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

### v3.3 User Feedback Update

Handled in the v3.3 feedback implementation:

- Pull current schema versions from `config/schema_version.json`.
- Keep missing question schema versions as legacy `1` while generated question rows use the configured question schema.
- Grade strongest wrong-service near misses as `C`.
- Update the answer rubric for the wrong-service near-miss rule.
- Add a release-note chart for expected grade distribution by letter.
- Refresh setup-generated artifacts after implementation.
- Review `config/data/curated_training_data.json` and `config/data/user_feedback.v3.json`.

### User Feedback Follow-Ups

- Add an explanatory question or feedback note contrasting S3 lifecycle policies with S3 bucket policies.
- Add a major SNS vs. SQS comparison question that teaches pub/sub fan-out versus queue-based polling/worker processing.
- Add a vertical-scaling versus horizontal-scaling question for EC2 and Auto Scaling concepts.
- Review artifact-review prompts that may give away the expected issue in the question wording, especially SDK pagination examples.
- Improve learner feedback when the answer is essentially unrelated so `suggested_improvements` explains how to move toward the target concept.
- Fix duplicate DynamoDB documentation links in the documentation/source section.

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
