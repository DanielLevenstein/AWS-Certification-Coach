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

# Phase 1 Model Stabilization
## v3.prototype.0 Design switch to sentence-transformers architecture
Add documentation for new model architecture and lock downgrading metrics
## v3.prototype.1 Audit existing documentation
Audit existing documentation to ensure it matches to design.
Completed: documentation was reconciled with the v3 semantic grading design and data boundaries.
## v3.prototype.2 Initial implementation
SentenceTransformer semantic normalization plus a supervised A–F classifier
Completed: implemented as the shared A/B/C/D/F semantic relationship classifier.
## v3.prototype.3 Lock down training metrics.
Lock down training metrics so they are comparable with an old model.
Completed: metric definitions, benchmark provenance, schema-v3 output, and release gates are frozen.


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
