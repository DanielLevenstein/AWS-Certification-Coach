# AWS-Certification-Coach
AI study partner for AWS certification exams

## Setup

Install the project in editable mode so the `src/` package imports work from Streamlit, tests, and command-line scripts:

```bash
python3 -m pip install -e .
```

Then run the app:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest
```

Train the answer classifier and enforce the 90% minimum gate:

```bash
python scripts/train_answer_classifier.py --min-accuracy 0.90
```

The default training command uses `data/questions/transformed_freeform_generated.json` and `data/training/answer_classification_generated.json`, which currently contain 100 self-authored sample questions and 800 labeled answer examples.

Final verification data is stored separately under `data/verification/`. Do not use that directory for training.

Generate optional partial-credit examples in a separate folder:

```bash
python scripts/generate_partial_answer_artifacts.py
```

This writes `data/training/partial_answer_ratings_generated.json` and `data/verification/answers/partial_answer_ratings_holdout.json` with continuous `rating` values from 0 to 1 and a `rating_bucket` field that preserves the original 0.75, 0.50, or 0.25 category. It is not used by the current binary classifier training command.

Refresh the app's small sample question set from the generated training questions:

```bash
python scripts/select_sample_questions.py --count 10
```

Use the trained classifier in the app:

```bash
export AWS_COACH_EVALUATOR_PROVIDER=trained_classifier
export AWS_COACH_CLASSIFIER_MODEL_PATH=models/answer_classifier.json
streamlit run app.py
```

## Evaluator Configuration

V1 defaults to the trained classifier evaluator after `models/answer_classifier.json` has been generated.

For LLM-based evaluation, use OpenAI with the configured default model:

```bash
export AWS_COACH_EVALUATOR_PROVIDER=openai
export OPENAI_API_KEY=...
streamlit run app.py
```

The recommended starting model is `gpt-5.4-mini` because answer grading needs reliable instruction following and useful feedback, but not the full cost of the flagship model for every response. Use `gpt-5.5` when evaluation quality matters more than latency or cost.

Provider, model, and hyperparameters are configured in `config/evaluator_default.json`. Common overrides:

```bash
export AWS_COACH_OPENAI_MODEL=gpt-5.5
export AWS_COACH_OPENAI_TEMPERATURE=0
export AWS_COACH_OPENAI_MAX_OUTPUT_TOKENS=1200
export AWS_COACH_OPENAI_REASONING_EFFORT=medium
```

## Question Transformation

Source multiple-choice artifacts should live in `data/questions/source_multiple_choice_*.json`. Transformed freeform artifacts preserve the original MCQ under `original_multiple_choice`.

Run the offline transformer with a stronger model:

```bash
python scripts/transform_questions.py \
  --input data/questions/source_multiple_choice_sample.json \
  --output data/questions/transformed_freeform_sample.json \
  --provider openai \
  --model gpt-5.4
```

For local smoke tests without API calls:

```bash
python scripts/transform_questions.py \
  --input data/questions/source_multiple_choice_sample.json \
  --output /tmp/transformed_freeform_sample.json \
  --provider heuristic
```
