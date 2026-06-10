# AWS-Certification-Coach

AI study partner for AWS certification exams

## Goal

AWS Certification Coach is a lightweight AI-powered study app for AWS certification practice. It presents pre-generated questions, evaluates learner answers with the trained local classifier or a configured LLM provider, and returns structured coaching feedback.

This project was based on a previous project called AWS-Documentation-Rag.
This version intentionally removes the runtime RAG stack from the earlier prototype.
There is no document ingestion, FAISS index, vector database, or embedding model in the deployed app.

Certification content is generated and reviewed offline, then served from a simple question repository.

### UX Flow

1. The learner opens the Streamlit app.
2. The learner selects certification, domain, and difficulty filters.
3. The app starts or resets a `QuizSession`.
4. The app displays the current `Question`.
5. The learner submits a free-text answer.
6. `EvaluationService` builds a prompt with `EvaluationPromptBuilder`.
7. The selected evaluator provider returns JSON feedback.
8. `EvaluationResponseParser` converts the response into an `EvaluationResult`.
9. The UI displays the result and records an `AnsweredQuestion`.
10. The learner advances to the next question until the filtered set is complete.

## Training Data Generation

The V1 training data is generated offline from self-authored, exam-style AWS scenarios. The project does not copy real exam dumps, paid practice-test text, or restricted AWS Skill Builder content. AWS exam guides and documentation are used as style and scope references, while the local artifacts are generated specifically for this project.

The generation flow starts with service-level scenario specs in `scripts/generate_sample_training_artifacts.py`. Each spec defines the target AWS service or feature, certification, domain, difficulty, expected purpose, key concepts, and plausible distractors. The script turns those specs into original multiple-choice questions, then converts them into freeform recall prompts so learners must explain the answer instead of recognizing it from choices.

Each generated question keeps its source-style multiple-choice item in the same JSON row under `original_multiple_choice`. The same row also stores answer examples used for model training:

- `binary_answers`: correct answers, paraphrases, shortened correct answers, distractor answers, generic wrong answers, and near-miss wrong answers.
- `wrong_answers`: explicit wrong-answer examples based on the multiple-choice distractors.
- `partial_answers`: continuous partial-credit examples with ratings between `0` and `1`, plus a coarse `rating_bucket` for provenance.

Training and verification data are generated separately:

- `data/training/questions_with_answers_generated.json`: training artifact used by the classifier and partial-credit regressor.
- `data/verification/questions_with_answers_holdout.json`: holdout artifact reserved for final verification and not used by training scripts.
- `data/questions/sample_questions.json`: app-facing question bank generated independently from training labels and grounded with AWS documentation source URLs.

The binary classifier treats `.25` partial-credit examples as explicit negatives, so very weak answers are rejected even when they mention a broad service family. The partial-credit regressor is trained separately against the continuous `rating` values using mean squared error. This keeps full-answer correctness and partial-credit estimation measurable as different tasks.

To regenerate the artifacts cleanly:

```bash
rm -rf data models
python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80
python scripts/train_answer_classifier.py --min-accuracy 0.90
python scripts/train_partial_answer_regressor.py
```

## Releases

### v1.0.0 Initial Release

#### Model Performance

| Full Answer Evaluation | Value |
| --- | ---: |
| Accuracy | 97.39% |
| Precision | 97.19% |
| Recall | 97.83% |
| Examples | 1150 |
| Evaluation mode | leave-one-question-out |

| Partial Credit Regressor | Value |
| --- | ---: |
| MSE | 0.0193 |
| MAE | 0.1006 |
| Examples | 500 |
| Evaluation mode | leave-one-question-out |

| Classifier TP | Classifier FP | Classifier TN | Classifier FN |
| ---: | ---: | ---: | ---: |
| 587 | 17 | 533 | 13 |

#### Scope

Certifications:

- Cloud Practitioner
- Solutions Architect Associate

Domains:

- Analytics
- Application Integration
- Billing
- Compute
- Database
- Governance
- Integration
- Networking
- Operations
- Resilient Architectures
- Security
- Storage

Difficulty:
- Easy
- Medium

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

Regenerate local training, holdout, and app sample artifacts:

```bash
python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80
```

Train the deployed answer classifier and enforce the 90% minimum gate:

```bash
python scripts/train_answer_classifier.py --min-accuracy 0.90
```

The default training command uses `data/training/questions_with_answers_generated.json`, which contains 100 self-authored freeform questions, original multiple-choice provenance, binary answer examples, wrong answers, and continuous partial-answer ratings.

Train the partial-credit regression model and report mean squared error:

```bash
python scripts/train_partial_answer_regressor.py
```

Print a single release-note friendly model performance summary:

```bash
python scripts/release_metrics.py
```

Final verification data is stored separately in `data/verification/questions_with_answers_holdout.json`. Do not use that file for training.

Use the trained classifier in the app:

```bash
export AWS_COACH_EVALUATOR_PROVIDER=trained_classifier
export AWS_COACH_CLASSIFIER_MODEL_PATH=models/answer_classifier.json
streamlit run app.py
```

## Docker

Build the container image:

```bash
docker build -t aws-certification-coach:latest .
```

Run the app on port 8501:

```bash
docker run --rm -p 8501:8501 aws-certification-coach:latest
```

The image includes the generated sample questions and trained model artifacts, so the default app path runs without an API key.

## Render Deployment

- Runtime: Docker
- Port: `8501`
- Health check path: `/_stcore/health`
- Default evaluator: `trained_classifier`
- API key requirement: none for the default classifier path; set `OPENAI_API_KEY` only when using the OpenAI provider.

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

Source multiple-choice artifacts may live in `data/questions/source_multiple_choice_*.json`. Transformed and generated app artifacts preserve the original MCQ under `original_multiple_choice`. The generated training and holdout files keep each freeform question and its answer examples together in one combined JSON row.

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
