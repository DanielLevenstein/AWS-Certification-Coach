# Question Data Sources

## Recommended Sources

1. AWS Certification Official Practice Question Sets

   AWS says these free 20-question sets are developed by AWS and demonstrate the style of certification exams. They include exam-style questions, detailed feedback, and recommended resources. These are the best source for calibrating question style, but their usage terms should be reviewed before storing, redistributing, or training on copied text.

2. AWS Certification Official Practice Exams

   AWS describes these as practice exams with the same question style and rigor as certification exams, exam-style scoring, answer-choice feedback, and recommended resources. These are likely the strongest quality signal, but they are subscription content and should not be copied into this repository unless the license explicitly allows it.

3. AWS Exam Prep Courses and Exam Readiness Webinars

   AWS exam prep courses review topic areas and sample certification questions by domain. These are useful for understanding domain coverage and common scenario framing. Use them to guide self-authored questions unless reuse rights are explicit.

4. AWS Exam Guides

   Exam guides define domains, task statements, and in-scope services. They are useful for labeling generated questions and ensuring coverage, but they are not a question bank by themselves.

5. Self-authored Exam-Style Questions

   This is the safest default for local artifacts. Use official AWS exam guides, AWS documentation, and Skill Builder style observations to write original questions, then transform them into freeform recall prompts.

6. User-Owned Notes and Review Material

   Notes from study sessions can be converted into question candidates if the user owns the content. Avoid copying third-party paid practice-test wording.

## Sources to Avoid Without Permission

- Dumps of real exam questions.
- Paid practice-test content copied from third-party providers.
- Scraped Skill Builder or practice exam content where terms do not allow reuse.
- Any source that claims to contain actual exam questions.

## Data Policy for This Project

- Store provenance for every imported question.
- Keep the original multiple-choice item attached to the transformed freeform question.
- Prefer self-authored content unless the source license is explicit.
- Do not train or distribute on restricted practice-test content without permission.
- Treat official AWS material as style guidance unless reuse terms are confirmed.

## Artifact Shape

Source multiple-choice artifacts may live in `data/questions/source_multiple_choice_*.json`.

Generated training artifacts live in `data/training/questions_with_answers_generated.json` and preserve the original item under `original_multiple_choice`.

Final holdout artifacts live in `data/verification/questions_with_answers_holdout.json` and must stay separate from training data.

Each combined question row can include `binary_answers`, `wrong_answers`, and `partial_answers` so human review cases can be added next to the source question they validate.
