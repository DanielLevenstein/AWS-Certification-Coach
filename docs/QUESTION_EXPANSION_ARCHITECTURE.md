# Question Quality Expansion Architecture

## Overview

The current version of AWS Certification Coach focuses on multiple-choice questions and AI-assisted evaluation of freeform responses. Initial testing identified two major limitations:

1. The multiple-choice question pool lacks sufficient variety and begins repeating concepts too frequently.
2. Existing question formats do not adequately test architectural reasoning or service selection tradeoffs that commonly appear on AWS certification exams.

This document defines the Phase 1 question-quality architecture from `docs/QUESTION_IMPROVEMENT_ROADMAP.md`: increase question diversity, improve distractors, add distractor classifications, and improve exam realism. Later roadmap phases can build on this foundation for code/configuration review, tradeoff analysis, and advanced feedback.

## Motivation

Many AWS certification practice platforms focus primarily on memorization and answer recognition.

Real AWS certification exams frequently require candidates to:

- Compare multiple AWS services.
- Evaluate tradeoffs between competing solutions.
- Select the best solution among several technically valid options.
- Understand cost, scalability, reliability, and operational implications.

These skills are challenging to evaluate using traditional multiple-choice questions alone.

Introducing structured freeform service-selection, service-comparison, and architecture-tradeoff questions provides a way to evaluate conceptual understanding while differentiating AWS Certification Coach from traditional exam simulators.

## Standard Language

Use the same language as `docs/QUESTION_EXPANSION_FEATURE.md` and `docs/ANSWER_RUBRIC.md`.

- `question quality`: the overall app-facing quality of a question batch, including diversity, distractor quality, domain coverage, exam realism, and source safety.
- `question fidelity`: release-facing score for generated question quality. It may combine `concept fidelity`, `exam-style fidelity`, distractor quality, technical correctness, and source safety.
- `concept fidelity`: whether the generated question preserves the intended AWS concept, service boundary, decision point, and reasoning pattern.
- `exam-style fidelity`: whether the generated question resembles permitted Developer Associate calibration patterns and requires applied exam reasoning.
- `learner-answer grading`: A/B/C/D/F grading of a learner response. This is separate from question fidelity.
- `AWS-valid`: the question and reference answer are technically accurate according to AWS documentation.
- `exam-valid`: the question resembles a permitted Developer Associate exam-style calibration pattern and tests the expected domain reasoning.

Use A/B/C/D/F only for learner-answer grades. Use 0-100 percentages or accept/revise/reject decisions for generated-question review.

## Goals

### Improve Question Diversity

Expand the AWS Developer Associate question bank with a larger number of realistic exam-style questions.

#### Success Criteria

- Reduced question repetition.
- Increased scenario coverage.
- Broader service coverage.

### Improve Exam Realism

Questions should better reflect the style and complexity of AWS certification exams.

#### Success Criteria

- Increased use of scenario-driven prompts.
- More realistic distractor answers.
- Greater emphasis on architectural reasoning.

### Add Distractor Classifications

Generated multiple-choice provenance should classify each incorrect answer so the project can measure distractor quality and later provide better feedback.

#### Success Criteria

- Incorrect options include `distractor_classifications`.
- Distractor rationales explain why each option is tempting and why it is not the best answer.
- Plausible distractors are distinguished from wrong-service-category and nonsensical distractors.

## Rollout Recommendation

Ship this in phases:

1. Expand scenario-based Developer Associate multiple-choice and freeform service-selection questions first.
2. Add distractor classification and rationales to generated multiple-choice provenance.
3. Add service-comparison questions for high-confusion pairs such as SQS/EventBridge, SNS/SQS, Secrets Manager/Parameter Store, CodeBuild/CodeDeploy, and DynamoDB/RDS.
4. Add architecture tradeoff questions only after the freeform evaluator can support multiple acceptable positions.
5. Add release metrics for question type distribution, Developer Associate domain coverage, and question fidelity.

This order reduces repetition quickly while avoiding a large answer-grading expansion before the question bank has enough structured metadata.

### Release And Test Criteria

Before merging a question-expansion batch:

- Regenerate local artifacts with `./clean.sh` and `./setup.sh`.
- Confirm `data/`, `scripts/data/`, and `metrics/` are not staged.
- Verify Developer Associate domain distribution.
- Verify each generated question has source provenance.
- Verify question-fidelity score meets the release threshold.
- Human-review a sample for both AWS-valid and exam-valid status.
- Confirm answer-training rows and final verification rows remain separate.

Suggested release metrics:

- Total app-facing question count.
- Developer Associate question count.
- Question count by `question_type`.
- Developer Associate domain coverage.
- Average question fidelity.
- Average concept fidelity.
- Average exam-style fidelity.
- Hard rejection counts from review.

### Open Architecture Questions

- Should multiple-choice remain visible in the main app flow, or should it primarily serve as provenance for freeform prompts?
- Should tradeoff questions allow multiple valid recommendations, or should each prompt be constrained to one best answer?
- What is the minimum acceptable Developer Associate domain distribution before deeper testing resumes?
- Should distractor quality affect only question-fidelity scoring, or should it also influence learner feedback for wrong multiple-choice answers?
- Should service-comparison questions be generated from curated service pairs rather than individual source rows?

## Introduce Structured Freeform Questions

Provide freeform questions that require users to explain service selection, service comparisons, and tradeoff reasoning.

### Success Criteria

- Users explain reasoning rather than selecting an answer.
- Feedback identifies missing concepts.
- Questions reinforce architectural thinking.

## Question Types

### Traditional Multiple Choice

`question_type`: `multiple_choice`

Users select a single best answer.

Example:

- Which AWS service provides durable object storage?
- Which AWS database stores NoSQL data?

### Scenario-Based Multiple Choice

`question_type`: `scenario_multiple_choice`

Users evaluate a realistic engineering scenario.

Example:

An application experiences unpredictable traffic spikes and requires asynchronous request processing.

- Which AWS service should be introduced?

### Multi-Select Source Questions

`question_type`: `multi_select_source`

Users answer a freeform version of a source question that originally required choosing more than one option, such as "pick two out of five."

Example:

An application needs to process events asynchronously and retain failed messages for later inspection.

- Which TWO AWS features should be used?

In the app, the freeform prompt should remain the main question form factor. The original multi-select question should be shown as source provenance so the learner understands that the reference answer expects multiple required choices.

### Service Comparison Questions

`question_type`: `service_comparison`

Users compare two AWS services and explain tradeoffs.

Example:

Compare Amazon SQS and Amazon EventBridge.

Discuss:

- Primary use cases
- Advantages
- Limitations
- Situations where each service is preferred

### Architecture Tradeoff Questions

`question_type`: `architecture_tradeoff`

Users explain the benefits and drawbacks of a design decision.

Example:

A development team wants to migrate an EC2 workload to AWS Lambda.

Explain:

- Benefits
- Risks
- Limitations
- Cost implications

### Service Selection Questions

`question_type`: `service_selection`

Users recommend a solution and justify their choice.

Example:

A team needs a highly scalable session storage solution supporting millions of requests per day.

Which AWS service would you recommend and why?

## Multiple Choice Evaluation Enhancements

Current scoring treats all incorrect answers equally.

This does not accurately reflect how AWS certification questions are structured.

Many AWS exam questions contain:

- One best answer
- One plausible but suboptimal answer
- Several clearly incorrect answers

Learner-answer grading should distinguish between these cases with the shared A/B/C/D/F grade language in `docs/ANSWER_RUBRIC.md`. Question-fidelity review should score distractor quality separately from the learner's grade.

## Distractor Classification

Each question should classify incorrect answers.

- `classification`: `plausible_but_suboptimal`
- `classification`: `over_engineered`
- `classification`: `under_engineered`
- `classification`: `wrong_service_category`
- `classification`: `nonsensical`

### Distractor Categories

#### Plausible But Suboptimal

Technically valid solution but does not best satisfy requirements.

Example:

- Using SNS instead of SQS for durable asynchronous processing.

---

#### Over-Engineered

Would solve the problem but introduces unnecessary complexity.

Example:

- Using Step Functions for a simple queueing problem.

---

#### Under-Engineered

Addresses only part of the requirements.

Example:

- Using Lambda without persistence when durability is required.

---

#### Wrong Service Category

The selected service belongs to an unrelated problem domain.

Example:

- Choosing Route 53 to solve event processing requirements.

---

#### Nonsensical

The answer demonstrates a fundamental misunderstanding of the problem.

Example:

- Choosing CloudFront as a database solution.

---

## Learner-Answer Evaluation Framework

Freeform learner answers should be evaluated using concept coverage, scenario constraints, and reasoning quality rather than exact-answer matching.

---

## Required Concepts

Core ideas expected in a passing learner answer.

Example:

DynamoDB vs RDS

Required Concepts:

- Horizontal scalability
- Access patterns
- Latency characteristics

---

## Bonus Concepts

Additional details demonstrating deeper learner understanding.

Examples:

- Global tables
- Operational overhead
- Cost considerations

---

## Common Misconceptions

Known incorrect assumptions that should affect learner-answer grading.

Examples:

- DynamoDB supports arbitrary joins.
- Lambda has unlimited execution time.
- SNS provides durable queue semantics.

---

## Feedback Model

Instead of returning only a grade, feedback should include:

- `covered_concepts`: concepts successfully discussed by the learner.
- `missing_concepts`: expected concepts not mentioned.
- `misconceptions`: potential misunderstandings requiring correction.
- `improvement_suggestion`: specific recommendation for strengthening the response.

---

## Initial Service Coverage

Developer Associate focus:

- Lambda
- API Gateway
- S3
- DynamoDB
- IAM
- CloudWatch
- EventBridge
- SNS
- SQS
- ECS
- ECR
- Step Functions
- Secrets Manager
- Systems Manager Parameter Store

---

## Future Expansion

The framework should be reusable for:

- AWS Solutions Architect Associate
- AWS Data Engineer Associate
- AWS Machine Learning Engineer Associate

Question generation, scoring, and feedback systems should remain certification-agnostic wherever possible.

---

## Expected Outcomes

The next version of AWS Certification Coach should:

- Provide greater question variety.
- Better simulate AWS certification reasoning.
- Improve user understanding of AWS service tradeoffs.
- Differentiate the platform from traditional practice exams.
- Reduce reliance on heuristic grading as a standalone feature by embedding it into meaningful educational workflows.

### Overall Assessment

This architecture is directionally strong. It correctly identifies that question-count expansion alone will not solve the repetition problem if the new questions all test the same recognition pattern. The strongest part of the proposal is the shift toward service selection, tradeoff explanation, and plausible-but-suboptimal distractors.

The main architecture risk is scope blending. The document covers at least three related but distinct systems:

- App-facing question-bank expansion.
- Question-fidelity and exam-validity review for generated questions.
- Learner-answer evaluation for multiple-choice and freeform responses.

Those systems should share metadata, but they should not share scoring models, thresholds, or release gates without explicit contracts.

### Recommended Architectural Boundaries

Keep `question_fidelity` separate from learner-answer grading.

Question fidelity should answer:

- Is this generated question AWS-valid?
- Is this generated question exam-valid?
- Does it preserve the intended source concept, service boundary, and reasoning pattern?
- Is the generated wording self-authored and safe to ship?

Learner-answer grading should answer:

- Did the learner identify the correct service or design choice?
- Did the learner explain the required concepts?
- Did the learner include misconceptions?
- How useful should the feedback be for the next attempt?

These two flows can use similar evidence fields, such as covered concepts and misconceptions, but they should remain separate in code, metrics, and release notes.

### Question Type Contract Notes

The proposed question types should have an explicit schema before implementation. A useful minimum contract would include:

- `question_type`: `multiple_choice`, `scenario_multiple_choice`, `multi_select_source`, `service_selection`, `service_comparison`, `architecture_tradeoff`, or `artifact_review`.
- `question_category`: a graph/taxonomy category such as `security_identity`, `integration_workflows`, `observability_governance`, `cost_tradeoff`, `scaling_performance`, `resilience_recovery`, `data_analytics`, `networking_delivery`, or another configured category.
- `certification` and `exam_code`.
- `domain` and, when available, exam-guide task statement.
- `difficulty`.
- `question`.
- `reference_answer`.
- `required_concepts`.
- `bonus_concepts`.
- `common_misconceptions`.
- `source_examples`.
- `exam_calibration`.
- `question_fidelity`, with `concept_fidelity` and `exam_style_fidelity` when reported separately.

Multiple-choice questions additionally need:

- `options`.
- `correct_option_ids`.
- `distractor_rationales`.
- `distractor_classifications`.
- `best_distractor`, when applicable.

Multi-select source questions additionally need:

- `selection_instruction`, such as `Choose TWO`.
- `required_selection_count`.
- Multiple `correct_option_ids`.
- A reference answer that explains every required correct option.

Freeform tradeoff questions additionally need:

- `acceptable_positions`, when more than one answer can be valid.
- `decision_criteria`, such as cost, operational overhead, latency, durability, scalability, or security.
- `must_not_claim`, for misconceptions that should trigger strong feedback.

### Distractor Classification Notes

The distractor taxonomy is useful and should become part of the source metadata, not only the rendered multiple-choice question. For each distractor, store:

- The category.
- Why it is tempting.
- Why it is not the best answer.
- Which missing requirement disqualifies it.

This is especially important for Developer Associate questions, where the difference between services is often about operational semantics rather than broad architecture. For example, SNS versus SQS, Lambda destinations versus SQS DLQs, Parameter Store versus Secrets Manager, or CodeBuild versus CodeDeploy.

### Tradeoff Question Scoring Notes

Tradeoff questions should avoid a single exact-answer rubric unless the prompt is intentionally service-selection focused. Many architecture tradeoff prompts can have more than one defensible answer depending on constraints.

Recommended scoring dimensions:

- Requirement coverage: Did the learner address all stated constraints?
- Service-boundary accuracy: Did the learner distinguish the services correctly?
- Tradeoff reasoning: Did the learner explain benefits, limitations, and when each option fits?
- Risk and misconception handling: Did the learner avoid false claims?
- Recommendation quality: If a recommendation is requested, is it justified by the scenario?

For release metrics, keep these learner-answer metrics separate from `question fidelity`. A generated question can be high quality even if the answer grader for that question type still needs work.

### AWS-Valid Versus Exam-Valid Gate

Add an explicit gate that rejects generated questions that are only AWS-valid.

AWS-valid means the question and reference answer are technically correct, according to AWS documentation.

Exam-valid means the question resembles permitted AWS certification calibration patterns and tests the intended domain reasoning.

Examples of AWS-valid but not exam-valid questions:

- Trivia about a service limit with no scenario.
- A question where all distractors are obviously unrelated.
- A prompt that asks for broad architecture design when the target is Developer Associate implementation detail.
- A service comparison that does not force a decision or explain a tradeoff.

### Source Safety Notes

This document should explicitly carry forward the source policy from `docs/QUESTION_EXPANSION_FEATURE.md`.

Do not use exam dumps, copied paid practice-test content, restricted Skill Builder text, or source material whose terms do not allow calibration use. Official or practice calibration should be summarized as metadata rather than copied into app-facing prompts unless the license clearly allows storage and reuse.

Generated questions should be self-authored from public AWS documentation concepts, exam-guide objectives, and permitted calibration notes.
