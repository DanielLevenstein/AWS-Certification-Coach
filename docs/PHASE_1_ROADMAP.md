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

# Phase 1 Planning And Rubric Stabilization
## Rubric Stabilization
Target Version: 2.2.3

Purpose: finish the code-free design pass before changing implementation behavior.
Documentation Changes:

- Review and finalize `docs/QUESTION_EXPANSION_ARCHITECTURE.md`.
- Review and finalize `docs/ANSWER_RUBRIC.md`.
- Review and finalize `docs/QUESTION_EXPANSION_FEATURE.md`.
- Confirm the shared A/B/C/D/F grade language for all learner-answer formats.
- Confirm that question-fidelity scoring remains separate from learner-answer grading.
- Confirm how multi-select source questions are represented when transformed into freeform prompts.
- Decide whether multiple-choice should remain visible in the main app flow or primarily serve as source provenance.
- Decide the minimum Developer Associate domain distribution needed before deeper manual testing resumes.
Exit criteria:

- Architecture and rubric docs are internally consistent.

## Answer Grading Stabilization
Target Version: 2.2.4

Coding Changes:
- Retrain existing questions on new rubric and determine baseline performance.
- Determine which columns should be maintained in the RELEASE_NOTES.md table going forward.
- Evaluate `curated_training_data.json` and suggest answer updates based on the evaluation rubric.
- Do not add any additional question types at this stage; standardize the evaluation rubric for the existing questions.

Exit criteria:

- Grading fidelity on existing questions should reach over 90% for accuracy, precision, and recall.
- Identify why Training Accuracy is lower than other metrics and consider removing it from release notes if it continues to fall behind.

Publish the app to Docker and GitHub after this stabilization step to avoid getting stuck in an infinite design loop.
Validate app in prod to ensure that new AWS Developer Certification questions display as expected. 


## Answer Rubric Data Contract
Target Version: 2.3.1

Purpose: introduce the data shape needed for consistent answer grading without changing the learner experience too much at once.

- Add a question-type field for app-facing questions.
  - `multiple_choice`
  - `scenario_multiple_choice`
  - `multi_select_source`
  - `question_category`
  - `service_comparison`
  - `architecture_tradeoff`
- Add rubric metadata fields to generated question artifacts.
  - `required_concepts`
  - `bonus_concepts`
  - `common_misconceptions`
  - `acceptable_answers`
  - `must_not_claim`
- Create a clean dataset with exact letter grade answer examples for testing newly implemented rubric.
- Add a flag to release notes to allow strict grading where the exact letter grade match is required.

Exit criteria:

- Existing questions still load.
- New rubric metadata is available to answer grading and feedback code.
- Unit tests pass.
- Release notes include schema and metric results.

# Phase 2 Code & Configuration Review
Release Target v2.4.0
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
