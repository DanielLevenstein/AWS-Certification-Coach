# Calibration And Review

Use permitted exam-style calibration material to decide whether generated questions are exam-valid, not merely AWS-valid.

## Allowed Calibration Sources

- AWS public exam guides and objective descriptions.
- AWS official sample questions.
- AWS official practice-question previews when terms allow local review for calibration.
- Self-authored AWS scenarios built from public documentation.

Do not use exam dumps, copied paid practice banks, restricted Skill Builder question text, or any source whose terms do not allow the intended use.

## Calibration Metadata

Store summarized metadata and notes rather than copied restricted text:

- `source_name`
- `source_url`
- `source_license_notes`
- `allowed_use`
- `source_type`
- `certification`
- `domain`
- `task_statement`
- `services`
- `concepts`
- `difficulty`
- `exam_style_notes`
- `distractor_pattern`
- `reasoning_pattern`

## Human Review Questions

Reviewers should answer:

- Is the generated question technically accurate?
- Does it test the same service boundary or decision point as the source concept?
- Does it feel like a Developer Associate question rather than Cloud Practitioner trivia or Solutions Architect design breadth?
- Are the distractors plausible and aligned with the intended misconception?
- Is the generated text clearly self-authored?
- Would a learner need applied AWS reasoning to answer it?

## Batch Acceptance

Accept a generated batch only when:

- The average fidelity score meets the release threshold.
- No hard rejection rule is present in sampled questions.
- Human sample review confirms both AWS-valid and exam-valid status.
- Release notes explain any score below the project quality standard.
