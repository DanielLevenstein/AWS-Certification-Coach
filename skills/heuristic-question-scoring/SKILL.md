---
name: heuristic-question-scoring
description: Design, review, and document heuristic question-fidelity scoring for AWS Certification Coach. Use when planning heuristic scoring for generated AWS questions, comparing generated questions to original or official AWS-style source sets, defining question fidelity metrics, reviewing AWS-valid versus exam-valid question quality, or preparing future implementation guidance without writing scoring code.
---

# Heuristic Question Scoring

## Overview

Use this skill to help future agents design heuristic scoring for generated AWS certification questions while the project is still in a code-free design phase. Keep the output focused on scoring dimensions, calibration evidence, data contracts, review criteria, and release metrics rather than implementation code.

## Workflow

1. Read `docs/QUESTION_EXPANSION_FEATURE.md` and confirm the scoring target is question fidelity, not learner-answer grading.
2. Identify the source set used for comparison: AWS documentation, exam-guide objectives, permitted official sample/practice calibration notes, or self-authored source scenarios.
3. Read `references/scoring-rubric.md` before defining scoring dimensions or thresholds.
4. Read `references/calibration-review.md` before writing validation, review, or release guidance.
5. Produce a code-free scoring design that separates concept fidelity from exam-style fidelity.
6. Include explicit rejection rules for copied restricted text, wrong-service concepts, poor distractors, and questions that are AWS-valid but not exam-valid.

## Guardrails

- Do not write implementation code unless the user explicitly says the project has moved out of the code-free section.
- Do not use exam dumps, copied paid practice banks, restricted Skill Builder question text, or any source whose terms do not allow calibration use.
- Do not claim generated questions are real-exam equivalent.
- Do not merge heuristic question-fidelity scoring with answer semantic scoring or heuristic answer scoring.
- Do not use final verification/test rows for training or threshold tuning.

## Output Shape

When asked for a heuristic scoring design, include:

- Inputs and required source metadata.
- Scoring dimensions and weights.
- Pass/fail gates.
- Human review requirements.
- Release metric names and interpretation.
- Test ideas or acceptance criteria, described without code.

## Required Distinction

Always distinguish:

- `AWS-valid`: the question and answer are technically accurate according to AWS documentation.
- `exam-valid`: the question resembles a permitted AWS Developer Associate exam-style calibration pattern and tests the expected domain reasoning.

Generated question batches should pass both checks before release.

## References

- Read `references/scoring-rubric.md` when defining or revising heuristic score dimensions, weights, gates, and metric names.
- Read `references/calibration-review.md` when planning calibration data, human review, batch acceptance, or release-note language.
