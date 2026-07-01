# Answer Rubric

## Purpose

This rubric defines a consistent answer-grading scale for AWS Certification Coach.

The same grade language should apply across `multiple_choice`, `scenario_multiple_choice`, `multi_select_source`, `service_selection`, `service_comparison`, `architecture_tradeoff`, and `artifact_review` questions. Individual question types may use different evidence fields, but the final grade should mean the same thing to learners throughout the app.

This rubric evaluates learner answers. It is separate from question-fidelity scoring, which evaluates whether generated questions are safe, accurate, and exam-valid before release.

## Standard Language

Use these terms consistently with `docs/QUESTION_EXPANSION_FEATURE.md` and `docs/QUESTION_EXPANSION_ARCHITECTURE.md`:

- `learner-answer grading`: A/B/C/D/F grading of a learner response.
- `question fidelity`: release-facing score for generated question quality. It is not a learner grade.
- `concept fidelity`: whether a generated question preserves the intended AWS concept, service boundary, decision point, and reasoning pattern.
- `exam-style fidelity`: whether a generated question resembles permitted Developer Associate calibration patterns and requires applied exam reasoning.
- `AWS-valid`: the question and reference answer are technically accurate, according to AWS documentation.
- `exam-valid`: the question resembles a permitted Developer Associate exam-style calibration pattern and tests the expected domain reasoning.

Use A/B/C/D/F only for learner answers. 
## Grading Principles

Grades should reflect conceptual distance from the best answer, not only whether the learner selected the exact expected option.

Use the grade to answer:

- Did the learner identify the right AWS service, feature, or pattern?
- Did the learner address the scenario constraints?
- Did the learner explain the key reasoning?
- Did the learner avoid major misconceptions?
- Did the learner choose a plausible but suboptimal solution, or a clearly unrelated one?

## Grade Scale

| Grade | Meaning |
|:------|:--------|
| A | Correct answer. Identifies the best AWS service, feature, or pattern; addresses the key scenario constraints; explains the important reasoning; avoids major misconceptions. |
| B | Mostly correct. Identifies the right service or pattern but misses one important constraint, tradeoff, qualifier, or detail needed for exam-ready reasoning. |
| C | Partially correct. Points a developer toward the right AWS service or implementation path, but misses an important qualifier, feature name, or condition. |
| D | Minimal credit. Stays related to the AWS domain or scenario area, but would not reliably lead to the right implementation. |
| F | Incorrect. Uses the wrong domain or service, contradicts the requirements, gives a nonsensical answer, includes a severe misconception, or provides no meaningful AWS reasoning. |

## Multiple-Choice Mapping

Multiple-choice grading should use the distractor meaning, not only right or wrong.

| Option Type | Default Grade | Notes |
|:------------|:--------------|:------|
| Best answer | A | The selected answer satisfies the stated requirements better than the alternatives. |
| Best wrong service-name distractor | C | The selected answer names the strongest plausible wrong AWS service or feature, such as a near-miss option marked by wording like `only` or `alone`, but it misses the best service boundary for the scenario. |
| Plausible but suboptimal distractor | C | The selected answer is technically related, but misses a key requirement or tradeoff. |
| Over-engineered distractor | C or D | Use C when it would work but is unnecessarily complex. Use D when complexity creates operational or cost concerns that conflict with the scenario. |
| Under-engineered distractor | D | The answer addresses part of the problem but fails an important requirement such as durability, security, scaling, or operational control. |
| Wrong service category | F | The answer solves a different type of problem. |
| Nonsensical distractor | F | The answer shows a fundamental misunderstanding of AWS service purpose or scenario requirements. |

Plausible distractors should not automatically receive C or D credit. They earn partial credit only when they show valid concept recognition.

## Multi-Select Source Question Mapping

Some AWS-style source questions require more than one correct option, such as "Choose TWO."

In AWS Certification Coach, these questions should still be transformed into freeform prompts. The original multi-select question should be preserved and displayed as source provenance so the learner understands that the reference answer expects multiple required services, features, or patterns.

For freeform grading, assign the learner grade based on how completely the response covers the required correct options:

| Freeform Coverage | Default Grade | Notes |
|:------------------|:--------------|:------|
| Explains all required correct choices with accurate reasoning | A | The learner identifies each required service, feature, or pattern and explains why the choices work together. |
| Names all required correct choices with limited reasoning | B | The answer is directionally correct but lacks enough explanation for exam-ready understanding. |
| Explains one required correct choice well but misses another | C | The learner shows real concept knowledge but does not satisfy the full multi-select requirement. |
| Mentions one required correct choice weakly or mixes it with a wrong service | D | The answer has minimal relevant signal but fails most of the expected response. |
| Misses all required correct choices | F | The answer does not identify the expected services, features, or patterns. |

When source provenance is shown, the UI should make the original selection rule visible, for example `Choose TWO`. The learner-facing freeform prompt should also make clear when multiple parts are expected.

## Freeform Mapping

Freeform answers should use the same A through F scale, but the grade should be based on evidence in the learner response.

Recommended evidence fields:

- `identified_service`: the primary AWS service, feature, or pattern named by the learner.
- `covered_concepts`: required concepts the learner addressed.
- `missing_concepts`: required concepts the learner omitted.
- `scenario_constraints`: cost, security, latency, durability, scale, availability, deployment, or operational requirements addressed by the learner.
- `tradeoff_reasoning`: advantages, limitations, and service-boundary reasoning included in the answer.
- `misconceptions`: incorrect claims or unsafe assumptions found in the answer.

## Freeform Grade Guidance

### A Answers

An A answer should:

- Name the best service, feature, or pattern.
- Explain why it fits the scenario.
- Address the most important constraints.
- Include the core required concepts.
- Avoid major incorrect claims.

### B Answers

A B answer should:

- Name the right service, feature, or pattern.
- Show mostly correct reasoning, or name the correct service while giving incomplete or partially incorrect reasoning.
- Miss one meaningful detail, constraint, or tradeoff.
- Remain safe and technically accurate overall.

### C Answers

A C answer should:

- Point a developer toward the right AWS service or implementation path.
- Miss an important qualifier, feature name, condition, or service-specific behavior.
- Show enough scenario understanding that the answer is more than just a related AWS keyword.
- Avoid severe misconceptions.

### D Answers

A D answer should:

- Mention a relevant AWS concept.
- Stay related to the domain but fail to identify a reliable implementation path.
- Provide very limited reasoning or a solution that would need substantial correction before implementation.
- Be too incomplete to trust as an exam-ready answer.
- Avoid being entirely unrelated or nonsensical.

### F Answers

An F answer should be assigned when the learner:

- Selects or recommends a clearly wrong service category.
- Contradicts an explicit scenario requirement.
- Makes a severe AWS misconception.
- Provides an unsafe security recommendation.
- Gives no meaningful answer.

## Examples

Scenario: A workload needs durable asynchronous processing with backpressure between producers and workers.

| Learner Answer | Grade | Rationale |
|:---------------|:------|:----------|
| Use Amazon SQS because it provides a durable queue that decouples producers from consumers and lets workers process messages asynchronously. | A | Correct service and reasoning. |
| Use Amazon SQS to decouple the application. | B | Correct service, but limited reasoning about durability and backpressure. |
| Use Amazon SNS because it can send messages to subscribers. | C | Related messaging service, but misses durable queue semantics and worker backpressure. |
| Use Lambda because it can run asynchronous code. | D | Mentions a relevant compute concept, but fails the durable queue requirement. |
| Use Route 53. | F | Wrong service category. |

Scenario: A Lambda function needs non-secret configuration values that differ between development and production.

| Learner Answer | Grade | Rationale |
|:---------------|:------|:----------|
| Use Lambda environment variables for non-secret per-environment configuration values. | A | Correct feature and constraint handling. |
| Use Lambda environment variables. | B | Correct feature, but minimal explanation. |
| Use Systems Manager Parameter Store. | C | Plausible adjacent configuration service, but not the direct Lambda feature requested. |
| Store the values in CloudWatch Logs. | F | Wrong service purpose. |
| Hard-code the values in the function package. | F | Contradicts maintainable environment-specific configuration practice. |

## Tradeoff Question Guidance

Tradeoff questions may have more than one defensible answer. In those cases, grade the reasoning rather than forcing a single expected recommendation.

An answer can earn A credit when it:

- States a clear recommendation or comparison.
- Explains when each service or pattern is appropriate.
- Addresses the scenario constraints.
- Names meaningful tradeoffs.
- Avoids false claims.

For service-comparison questions, a learner can earn partial credit even without choosing a final service if the prompt asks only for comparison. For service-selection questions, the learner should make and justify a recommendation.

## Severe Misconceptions

Severe misconceptions should cap the grade at D or F depending on impact.

Examples:

- Claiming Lambda has unlimited execution time.
- Claiming SNS provides durable queue semantics by itself.
- Claiming DynamoDB supports arbitrary relational joins.
- Recommending public S3 bucket access when the scenario requires private temporary access.
- Treating IAM users and IAM roles as interchangeable for temporary credentials.

## Feedback Requirements

Feedback should explain the grade in learner-facing terms.

Each graded response should include:

- The assigned grade.
- Concepts the learner identified correctly.
- Missing concepts needed for a stronger answer.
- Misconceptions, if any.
- A concise improvement suggestion.
- A reference-quality answer or explanation.

Feedback should avoid saying only "wrong" when the learner selects a plausible distractor. It should explain what the distractor got right and which requirement made it suboptimal.

## Calibration Notes

Use this rubric consistently across question types but allow each question to define its own required concepts, bonus concepts, misconceptions, and acceptable answers.

Release accuracy should be calculated against the exact expected letter grade (`A`, `B`, `C`, `D`, or `F`), not broad grade bands such as `A/B` or `C/D`. A predicted `B` for an expected `A` is a calibration miss even though both are accepted answers.

Precision and recall may still be reported as accepted-answer diagnostics, where `A`, `B`, `C`, and `D` are accepted and `F` is rejected. Those diagnostics should not replace exact-letter semantic accuracy.

Do not tune grading thresholds against final verification data. Use curated examples and human review to calibrate borderline B/C and C/D cases.
