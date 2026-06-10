# Question Data Sources

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

App-facing questions live in `data/questions/sample_questions.json`. They should not include `binary_answers`, `wrong_answers`, or `partial_answers`; those fields are training-only labels. The app question bank should be generated independently from training data and should include source URLs for topic grounding.

Each combined question row can include `binary_answers`, `wrong_answers`, and `partial_answers` so human review cases can be added next to the source question they validate.
