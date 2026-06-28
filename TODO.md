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

## Question Expansion
Expand service-selection-template questions, so there is more than one question type present.
- Example categories:
- cost_tradeoff
- operational_complexity_tradeoff
- latency_tradeoff
- durability_availability_tradeoff
- managed_vs_self_managed_tradeoff
- event_driven_vs_batch_tradeoff
- security_boundary_tradeoff

### Specific question suggestions
- Add an explanatory question or feedback note contrasting S3 lifecycle policies with S3 bucket policies.
- Added initial SNS vs. SQS service-selection boundary cases that teach pub/sub fan-out versus queue-based polling/worker processing; revisit later for a dedicated service-comparison question type.
- Added an initial EC2 Auto Scaling service-selection boundary case for horizontal scaling versus vertical scaling; revisit later for richer scaling tradeoff questions.
- Add a Lambda environment variables wording case so answers that say "environmental variables" are recognized when the intended concept is Lambda environment variables.
- Review artifact-review prompts that may give away the expected issue in the question wording, especially SDK pagination examples.
- Added grading guard for answers that name the correct service but include materially wrong reasoning; the grade now reflects both the correct service hit and the incorrect claim.
- Added regression coverage so correct paraphrases are not downgraded merely because they reword the original question.
- Added grading guard so service-identification answers that describe the concept but omit the required AWS service or feature name do not receive a B-level grade.
- Improve learner feedback when the answer is essentially unrelated so `suggested_improvements` explains how to move toward the target concept.
- Improve `suggested_improvements` wording so it gives concrete next steps instead of generic "explain improvements" style feedback.
- Fixed repeated DynamoDB documentation labels in the documentation/source section by using option-specific labels when multiple links share the same service name.

Add service-oriented questions that directly ask the user to compare the pros and cons of two different services. 

### Knowledge base notes for expansion
- Treat the top-level `common_misconceptions` section as a legacy compatibility section for future code; leave it in place rather than moving code or data around.
- Expand the `services` section only when the next stage of question expansion identifies specific service metadata needed for generation, distractor quality, or feedback.

### Additional Feedback
Additional question generation feedback can be found in the feedback_text section of user_feedback.v3.json

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
