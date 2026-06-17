# Data Contracts

## Artifact Rules

- Keep raw source examples under `data/original_questions/`.
- Keep generated training, validation, and test artifacts under `data/generated/`.
- Keep app-facing questions under `data/questions/`.
- Keep curated human-reviewed feedback under `data/curated/`.
- Never commit generated `/data/`, `/scripts/data/`, or `/metrics/` artifacts.

## Split Integrity

- Training scripts may read training rows and optionally curated training feedback.
- Validation rows may guide checkpoint selection and threshold tuning.
- Final test rows must be used only for final reporting.
- App-facing question artifacts should not contain training-only answer labels.
- Tests should assert that training scripts do not default to final test paths.

## Question Fidelity Rows

Use a source concept bundle rather than copied exam text. Recommended source fields:

- `source_name`
- `source_url`
- `source_license_notes`
- `certification`
- `domain`
- `task_statement`
- `services`
- `concepts`
- `difficulty`

Recommended generated question fields:

- `question`
- `reference_answer`
- `key_concepts`
- `source_examples`
- `question_fidelity`

The fidelity model should compare the source concept bundle to the generated question and reference answer, then report covered, missing, and conflicting concepts.
