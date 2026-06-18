# AWS Certification Coach TODO

Current baseline: `v2.2.2`

Use minor releases for feature milestones, such as `v2.3.0` and `v2.4.0`.
Use patch releases for internal testing iterations, such as `v2.3.1` and `v2.3.2`.

The previous TODO was backed up to `docs/TODO_COPY.md` before this roadmap was created.

## Release Discipline

- Run `./clean.sh` before regenerating artifacts when schema or generated-data behavior changes.
- Run `./setup.sh` after cleaning to regenerate local test data.
- Run `./run_unit_tests.sh` before considering a milestone ready.
- Run release metrics before any commit that claims a release milestone.
- Update `docs/RELEASE_NOTES.md` for each release with a one-line change description and release metrics.
- Do not commit `data/`, `scripts/data/`, or `metrics/`.
- Do not push Docker images or create GitHub tags until a human reviews the changes.

## v2.2.3 Planning And Rubric Stabilization

Purpose: finish the code-free design pass before changing implementation behavior.
Documentation Changes:

- Review and finalize `docs/QUESTION_EXPANSION_ARCHITECTURE.md`.
- Review and finalize `docs/ANSWER_RUBRIC.md`.
- Confirm the shared A/B/C/D/F grade language for all learner-answer formats.
- Confirm that question-fidelity scoring remains separate from learner-answer grading.
- Confirm how multi-select source questions are represented when transformed into freeform prompts.
- Decide whether multiple-choice should remain visible in the main app flow or primarily serve as source provenance.
- Decide the minimum Developer Associate domain distribution needed before deeper manual testing resumes.
Exit criteria:

- Architecture and rubric docs are internally consistent.

## v2.2.5 Answer Grading Stabilization

Coding Changes:
- Retrain existing questions on new rubric and determine baseline performance.
- Determine which columns should be maintained in the RELEASE_NOTES.md table going forward.
- evaluate curated_training_data.json with suggested answer updates to make based on the evaluation rubric.
- Do not add any additional questions types at this stage standardize the evaluation rubric for the existing questions. 

Exit criteria:

- Grading fidelity on existing questions should reach over 90% for accuracy, precision, and recall.
- Identify why Training Accuracy is lower than other metrics and consider removing it from release notes if it continues to fall behind. 
- Grading should be updated to perform letter grade match based on evaluation rubric.

Release this version of the app to docker and GitHub as release/v2 to avoid getting stuck in an infinite design loop. 
Validate app in prod to ensure that new AWS Developer Certification questions display as expected. 

## v2.3.0 Answer Rubric Data Contract

Purpose: introduce the data shape needed for consistent answer grading without changing the learner experience too much at once.

- Add a question-type field for app-facing questions.
  - `multiple_choice`
  - `scenario_multiple_choice`
  - `multi_select_source`
  - `service_selection`
  - `service_comparison`
  - `architecture_tradeoff`
- Add rubric metadata fields to generated question artifacts.
  - `required_concepts`
  - `bonus_concepts`
  - `common_misconceptions`
  - `acceptable_answers`
  - `must_not_claim`
- Add answer-rubric grade definitions to the application domain model or grading layer.
- Preserve backward compatibility with existing `key_concepts` rows.
- Add tests that verify generated app-facing question artifacts include required rubric metadata where applicable.
- Add tests that verify training-only answer rows remain separate from app-facing question rows.

Patch iterations:

- `v2.3.1`: run generated-artifact validation and fix schema gaps.
- `v2.3.2`: run manual review on a small Developer Associate sample and update rubric boundaries for B/C and C/D cases.

Exit criteria:

- Existing questions still load.
- New rubric metadata is available to answer grading and feedback code.
- Unit tests pass.
- Release notes include schema and metric results.

## v2.4.0 Multi-Select Source Question Support

Purpose: support AWS-style "Choose TWO" source questions while keeping freeform answers as the primary UI.

- Extend original multiple-choice provenance to support multi-select instructions.
  - `selection_instruction`, such as `Choose TWO`
  - `required_selection_count`
  - multiple `correct_option_ids`
- Update the question generator so multi-select source rows produce freeform prompts that clearly expect multiple required choices.
- Update the source multiple-choice sidebar display so the user can see the original selection rule above the options.
- Update reference answers so they explain every required correct option.
- Update grading expectations so:
  - all required choices with accurate reasoning earns A,
  - all choices with weak reasoning earns B,
  - one strong required choice earns C,
  - one weak or mixed required choice earns D,
  - missing all required choices earns F.
- Add tests for multi-select provenance loading and sidebar rendering helpers.

Patch iterations:

- `v2.4.1`: manual-test transformed multi-select questions in the app.
- `v2.4.2`: tune prompt wording and reference answers based on manual-testing repetition or ambiguity.

Exit criteria:

- Multi-select source questions appear clearly in source provenance.
- Learners are not asked to interact with a multi-select UI unless a future product decision requires it.
- Unit tests pass.

## v2.5.0 Distractor Classification And Partial-Credit Feedback

Purpose: make wrong multiple-choice provenance useful for learner feedback and rubric calibration.

- Add distractor classification metadata.
  - `plausible_but_suboptimal`
  - `over_engineered`
  - `under_engineered`
  - `wrong_service_category`
  - `nonsensical`
- Add distractor rationales.
  - why the option is tempting,
  - why it is not the best answer,
  - which requirement disqualifies it.
- Map distractor categories to default grades from `docs/ANSWER_RUBRIC.md`.
- Update feedback generation so plausible distractors receive explanatory feedback rather than only "wrong" feedback.
- Add tests for distractor category parsing and grade mapping.

Patch iterations:

- `v2.5.1`: calibrate distractor grade defaults against curated examples.
- `v2.5.2`: update generated Developer Associate questions where distractors are too obvious or unrelated.

Exit criteria:

- Distractor metadata is present in generated source provenance.
- Feedback identifies why a plausible but suboptimal answer is not best.
- Release metrics include question type and distractor-classification coverage.

## v2.6.0 Service-Comparison Question Expansion

Purpose: generate freeform questions that ask learners to compare AWS services and explain tradeoffs.

- Define curated service pairs for high-confusion Developer Associate concepts.
  - SQS vs EventBridge
  - SNS vs SQS
  - Secrets Manager vs Systems Manager Parameter Store
  - CodeBuild vs CodeDeploy
  - DynamoDB vs RDS
  - Lambda destinations vs SQS dead-letter queues
- Generate service-comparison questions from curated service pairs rather than only individual source rows.
- Add rubric metadata for each service-comparison question.
  - shared concepts,
  - distinguishing concepts,
  - required tradeoffs,
  - common misconceptions.
- Update answer grading prompts or local grading logic so comparison answers are evaluated on service-boundary accuracy and tradeoff reasoning.
- Add tests that verify service-comparison questions preserve source provenance and do not copy restricted text.

Patch iterations:

- `v2.6.1`: manual-review comparison prompts for exam-validity.
- `v2.6.2`: tune answer feedback for missing comparison dimensions.

Exit criteria:

- Service-comparison questions are available in the app-facing question bank.
- Questions pass question-fidelity and human exam-valid review.
- Unit tests pass.

## v2.7.0 Architecture Tradeoff Question Support

Purpose: add broader freeform tradeoff questions only after the evaluator can handle multiple defensible answers.

- Define the `architecture_tradeoff` question contract.
- Add `acceptable_positions` for prompts where more than one recommendation can earn high credit.
- Add `decision_criteria`.
  - cost,
  - operational overhead,
  - latency,
  - durability,
  - scalability,
  - security,
  - deployment complexity.
- Update answer grading to reward reasoning quality instead of forcing one exact recommendation.
- Add tests for multiple acceptable answer paths.
- Human-review examples to confirm the prompts are exam-valid rather than open-ended design essays.

Patch iterations:

- `v2.7.1`: calibrate B/C and C/D grade boundaries for tradeoff answers.
- `v2.7.2`: update examples where prompts are too broad for certification practice.

Exit criteria:

- Architecture tradeoff answers can be graded consistently with the shared A/B/C/D/F rubric.
- Severe misconceptions cap grades at D or F.
- Unit tests pass.

## v2.8.0 Release Metrics And Coverage Reporting

Purpose: make question expansion measurable before larger manual-testing cycles.

- Add release metrics for:
  - total app-facing question count,
  - Developer Associate question count,
  - question count by `question_type`,
  - Developer Associate domain coverage,
  - average question fidelity,
  - average concept fidelity,
  - average exam-style fidelity,
  - hard rejection count from review,
  - distractor-classification coverage.
- Update release notes rendering to include new question-expansion metrics.
- Add tests for release metric calculation and rendering.

Patch iterations:

- `v2.8.1`: compare metrics before and after regeneration.
- `v2.8.2`: fix gaps found during release-note dry runs.

Exit criteria:

- Release notes can describe question quality and answer-rubric readiness without manual table edits.
- No generated data or metrics artifacts are staged.

## Future Release: Heuristic Answer Scoring Model

Purpose: implement a separate heuristic answer-scoring model after the rubric and metadata contracts are stable.

- Implement heuristic-based answer scoring as a separate model that returns an answer score between 0 and 100.
- Keep heuristic answer scoring separate from:
  - semantic answer scoring,
  - question-fidelity scoring.
- Ensure model weights are not shared with semantic scoring or question-fidelity scoring.
- Use proper train, validation, and test separation.
- Do not tune thresholds against final verification data.
- Use curated examples and human review to calibrate borderline grades.

Candidate version:

- `v2.9.0` if the v2.3-v2.8 roadmap is complete and stable.

## Backlog

- Decide whether app navigation should expose question type filters.
- Decide whether multiple-choice source provenance should be collapsible, sidebar-only, or shown after answer submission.
- Add authoring guidance for self-authored AWS-valid and exam-valid source rows.
- Add a human-review checklist for generated question batches.
- Expand Developer Associate source coverage beyond serverless, messaging, deployment, and data-access patterns.
