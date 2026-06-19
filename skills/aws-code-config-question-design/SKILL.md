---
name: aws-code-config-question-design
description: Design, review, and document AWS Certification Coach artifact-review questions for IAM policies, Lambda code, SDK usage, and CloudFormation or SAM templates. Use before making code changes for Phase 2 code and configuration review, when defining artifact question contracts, source safety rules, learner grading expectations, or release metrics for AWS code/configuration question batches.
---

# AWS Code Config Question Design

## Purpose

Use this skill when planning or reviewing Phase 2 artifact-review questions for AWS Certification Coach. Keep work code-free unless the user explicitly says implementation may begin.

## Workflow

1. Read `docs/PHASE_2_CODE_CONFIGURATION_REVIEW_DESIGN.md`.
2. Read `docs/ANSWER_RUBRIC.md` to keep learner-answer grades on the A/B/C/D/F scale.
3. Read `docs/QUESTION_EXPANSION_FEATURE.md` or `docs/QUESTION_EXPANSION_ARCHITECTURE.md` when question-fidelity, source policy, or exam-valid language is needed.
4. Read `references/artifact-review-rubric.md` before defining artifact metadata, rejection rules, or review criteria.
5. Identify the artifact family: IAM policy, Lambda code/configuration, SDK usage, or CloudFormation/SAM.
6. Produce a design, review, or acceptance checklist that separates generated-question fidelity from learner-answer grading.

## Guardrails

- Do not write runtime application code unless the user explicitly moves out of the design phase.
- Do not use exam dumps, copied paid practice-bank content, restricted Skill Builder text, private customer code, real secrets, or real incident artifacts.
- Do not require AWS credentials, local deployment, or code execution to answer or grade an artifact question.
- Do not mix question-fidelity scoring with learner-answer grading.
- Do not commit generated `/data/`, `/scripts/data/`, or `/metrics/` artifacts.

## Output Shape

When asked to design or review Phase 2 artifact questions, include:

- Target artifact family and scenario.
- Required artifact metadata.
- Expected issue and reference answer expectations.
- Required concepts, bonus concepts, common misconceptions, and `must_not_claim` items.
- AWS-valid and exam-valid review criteria.
- Source-safety notes.
- Release metrics or acceptance criteria when relevant.

## References

- Read `references/artifact-review-rubric.md` for artifact-family-specific metadata, hard rejections, and quality checks.

