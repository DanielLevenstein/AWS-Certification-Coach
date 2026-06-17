# v2.2.0 Enhanced Services Comparison Design

## Purpose

Version 2.2.0 expands AWS Certification Coach beyond recall-style freeform questions. The new question type asks learners to compare architectural tradeoffs between two or more plausible AWS services or features, especially when a source multiple-choice question has one best answer and one strong near-miss.

The goal is to help learners explain why the best answer is correct, why the next-best answer is less appropriate, and what scenario constraint changes the decision.

## Goals

- Generate comparison-style freeform questions from suitable multiple-choice source questions.
- Prefer source questions with plausible distractors that represent meaningful service-boundary tradeoffs.
- Increase the number of source multiple-choice questions sampled during generation so app questions feel less repetitive.
- Preserve the original multiple-choice provenance while presenting learners with a freeform comparison prompt.
- Add a release-note-ready concept coverage PNG that shows how generated questions cover services, domains, and concepts.
- Keep question-fidelity scoring separate from learner-answer grading.

## Non-Goals

- Do not replace the existing standard freeform transformation flow.
- Do not use exam dumps, copied paid practice-bank text, or restricted question text.
- Do not train answer-scoring models on final verification data.
- Do not treat comparison questions as real-exam equivalents.

## Candidate Source Questions

Comparison questions should come from source multiple-choice items where the wrong answers are not merely bad, unrelated, or syntactically invalid. The best candidates have:

- One clearly correct service, feature, or configuration.
- One plausible near-miss that is AWS-valid but weaker for the stated constraints.
- A scenario constraint that explains the tradeoff, such as latency, operational overhead, durability, consistency, event semantics, security boundary, deployment stage, or cost.
- Distractors that expose common misconceptions, such as choosing read replicas when the scenario needs backup or disaster recovery, choosing caching when the scenario needs persistence, or choosing a queue when the scenario needs pub/sub fanout.

Poor candidates should stay in the standard freeform pipeline or be rejected:

- The distractors are unrelated services.
- The correct answer is factual trivia rather than scenario reasoning.
- More than one answer could be equally correct without adding assumptions.
- The source item tests an AWS-valid concept but not an exam-valid Developer Associate decision pattern.

## Transformation Shape

The learner-facing prompt should ask for a direct comparison, not a hidden multiple-choice answer.

Recommended prompt pattern:

> In this scenario, compare `<best service or feature>` with `<near-miss service or feature>`. Explain why `<best>` is the better fit, why `<near-miss>` is tempting but weaker, and which scenario constraints drive the decision.

The generated row should preserve existing app fields and add comparison metadata:

- `question_type`: `service_comparison`
- `compared_services`: service or feature names compared in the prompt.
- `best_choice`: the original correct answer.
- `near_miss_choice`: the strongest plausible distractor.
- `tradeoff_concepts`: concepts that should appear in a strong answer.
- `comparison_rationale`: short author-facing explanation of the service boundary.
- `original_multiple_choice`: unchanged source MCQ provenance.
- `question_fidelity`: concept and exam-style fidelity result.

## Reference Answer Requirements

A strong reference answer should include:

- The best service or feature and the decisive scenario constraint.
- The near-miss service or feature and why it does not fully satisfy the scenario.
- At least one explicit tradeoff phrase, such as "lower operational overhead", "supports fanout", "isolates failed messages", "keeps reads close to users", or "does not provide durable storage".
- Any important AWS-specific boundary condition.

It should avoid:

- Restating only the original answer letter.
- Saying the near-miss is simply wrong without explaining why.
- Adding unrelated AWS services that were not part of the comparison.

## Sample Expansion Strategy

To reduce repetition, v2.2.0 should expand source sampling before transformation:

- Load all curated question files under `data/curated/` regardless of filename.
- Load generated feedback rows from `data/generated/generated_feedback.json`, `data/generated/generated_feedback.*.json`, and `data/generated/user_feedback.*.json`.
- Deduplicate by stable source ID when present, then by normalized question text.
- Track the number of eligible standard freeform candidates and service-comparison candidates separately.
- Prefer balanced sampling across certification, domain, service family, and difficulty.
- Cap repeated service pairs so the app does not overuse a single comparison, such as Lambda versus ECS or S3 replication versus backup.

Freeform user feedback should remain manual-review input for v2.2.0. It should not automatically train answer models until the feedback schema distinguishes question-generation feedback from answer-grading feedback.

## Concept Coverage PNG

Release notes should include a PNG generated from the app-facing question set. The chart should make coverage gaps visible at a glance.

Recommended chart panels:

- Domain distribution by question count.
- Top AWS concepts or services by occurrence.
- Question-intent mix, such as service selection, configuration decisions, troubleshooting, and service-comparison tradeoffs.
- Optional certification split when multiple certifications are present.

Suggested artifact name:

- `metrics/<timestamp>/question_domain_coverage.png` for domain coverage.
- `metrics/<timestamp>/question_intent_coverage.png` for question-intent coverage.
- `metrics/<timestamp>/question_certification_coverage.png` for certification split.
- `release/v2.2.0_question_*_coverage.png` for the first v2.2.0 release outputs.

Release-note language should describe the chart as concept coverage for the generated question bank, not as proof of exam equivalence.

## Question Fidelity And Review

Question fidelity remains a generated-question quality metric, not learner-answer grading. For comparison questions, fidelity should evaluate both source preservation and comparison quality.

Suggested scoring dimensions:

| Dimension | Weight | Purpose |
|:--|--:|:--|
| Concept fidelity | 30 | The comparison preserves the source service boundary and decision point. |
| Comparison quality | 25 | The prompt and reference answer explain the best answer versus the strongest near-miss. |
| Exam-style fidelity | 20 | The scenario resembles permitted Developer Associate calibration patterns. |
| Technical correctness | 15 | The answer is accurate according to AWS documentation. |
| Source safety | 10 | The generated text is self-authored and does not copy restricted source text. |

Hard rejection rules:

- The generated prompt copies restricted source wording.
- The best answer or near-miss points to the wrong AWS service or feature.
- The near-miss is not actually plausible.
- The comparison tests a different certification domain than the source target.
- The prompt is AWS-valid but lacks applied exam-style reasoning.
- The reference answer makes multiple services appear equally correct without explaining the deciding constraint.

Human reviewers should answer:

- Is the best answer technically correct?
- Is the near-miss plausible enough to teach a real tradeoff?
- Does the prompt ask the learner to compare reasoning rather than recall a service name?
- Does the reference answer explain both why the best answer wins and why the near-miss loses?
- Is the generated text clearly self-authored?

## Release Metrics

The existing release metrics should continue to report answer-scoring quality separately from generated-question quality.

For v2.2.0, add or retain:

- `Question Fidelity`: overall generated-question fidelity.
- `Comparison Fidelity`: average score for service-comparison questions only.
- `Comparison Candidate Count`: number of source MCQs eligible for comparison transformation.
- `Generated Comparison Question Count`: number of app-facing comparison questions generated.
- `Concept Coverage Charts`: paths to the domain, intent, and certification release PNG artifacts.

If `Comparison Fidelity` is below the quality standard, add a note below the release metrics table explaining whether the issue is concept fidelity, near-miss quality, technical correctness, or exam-style fit.

## Acceptance Criteria

- Comparison questions preserve original MCQ provenance.
- Standard freeform and comparison transformations can coexist in the app-facing question bank.
- Expanded source sampling reduces repeated prompts without mixing training, validation, and final verification data.
- Concept coverage PNG is generated and referenced from release notes.
- No files under `data/`, `scripts/data/`, `metrics/`, or `release/metrics/` are staged for source control.
- `./release_notes.sh --full v2.2.0` is run before the first v2.2.0 commit that implements the feature.
