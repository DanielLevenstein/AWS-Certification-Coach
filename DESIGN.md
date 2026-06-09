# AWS Certification Coach V1 Design

## V1 Feature Set

V1 should prove the core study loop without reintroducing RAG or account management.

Minimum features:

- Load certification questions from local JSON files.
- Filter questions by certification, domain, and difficulty.
- Start a single-user study session.
- Present one free-response question at a time.
- Accept a learner answer.
- Build a consistent evaluation prompt.
- Evaluate the answer through a narrow evaluator interface.
- Parse model feedback into score, missing concepts, improvements, coaching feedback, and a detailed correct answer.
- Track completed questions and score history for the current session.
- Display feedback and move to the next question.

Explicitly out of scope for V1:

- User accounts.
- Persisted progress.
- Runtime document ingestion.
- FAISS, embeddings, vector search, or RAG.
- Multi-certification recommendation logic.
- Payment, sharing, or admin features.

## UX Flow

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

## Proposed File Structure

```text
AWS-Certification-Coach/
  app.py
  ARCHITECTURE.md
  DESIGN.md
  README.md
  DATA_SOURCES.md
  pyproject.toml
  requirements.txt
  config/
    evaluator_default.json
  data/
    questions/
      source_multiple_choice_sample.json
      source_multiple_choice_generated.json
      sample_questions.json
      transformed_freeform_generated.json
      transformed_freeform_sample.json
    training/
      answer_classification_seed.json
      answer_classification_generated.json
      partial_answer_ratings_generated.json
    verification/
      answers/
        answer_classification_holdout.json
        partial_answer_ratings_holdout.json
      questions/
        source_multiple_choice_holdout.json
        transformed_freeform_holdout.json
  scripts/
    generate_sample_training_artifacts.py
    generate_partial_answer_artifacts.py
    select_sample_questions.py
    train_answer_classifier.py
    transform_questions.py
  src/
    aws_certification_coach/
      __init__.py
      domain.py
      evaluation/
        __init__.py
        factory.py
        prompting.py
        service.py
      llm/
        __init__.py
        local_llama.py
        openai_provider.py
      observability/
        __init__.py
        timing.py
      questions/
        __init__.py
        json_repository.py
      quiz/
        __init__.py
        session.py
      transforms/
        __init__.py
        mcq_to_freeform.py
      training/
        __init__.py
        answer_classifier.py
        dataset.py
        features.py
```

Moved reusable files:

- `shared/evaluation.py` -> `src/aws_certification_coach/evaluation/prompting.py`
- `shared/llm_runtime.py` -> `src/aws_certification_coach/llm/local_llama.py`
- `shared/timing.py` -> `src/aws_certification_coach/observability/timing.py`

The old `shared/` directory is removed after these moves. Reusable code now lives inside the application package where imports, tests, and future packaging can treat it as first-class app code.

## Core Classes

### Domain

- `Question`: immutable certification practice question loaded from JSON.
- `QuestionFilter`: optional certification, domain, and difficulty filters.
- `AnsweredQuestion`: a completed question plus learner answer and evaluation.
- `EvaluationResult`: structured evaluator output with score, missing concepts, improvements, feedback, and a detailed answer.
- `MultipleChoiceQuestion`: original exam-style source question preserved for provenance and post-answer review.
- `MultipleChoiceOption`: answer choice attached to an original multiple-choice question.

### Questions

- `JsonQuestionRepository`: loads and validates JSON question files.
  - `all() -> list[Question]`
  - `filter_questions(filters: QuestionFilter) -> list[Question]`
  - `available_certifications() -> list[str]`
  - `available_domains() -> list[str]`
  - `available_difficulties() -> list[str]`

### Quiz

- `QuizSession`: owns a single learner's in-memory session.
  - `current_question() -> Question | None`
  - `record_answer(question, user_answer, evaluation)`
  - `advance()`
  - `is_complete`
  - `score_history`
  - Randomizes question order when a session starts or resets.

### Evaluation

- `EvaluationPromptBuilder`: builds the provider prompt.
- `EvaluationResponseParser`: parses provider JSON into `EvaluationResult`.
- `EvaluatorProvider`: protocol for model providers.
- `EvaluationService`: coordinates prompt building, provider execution, and parsing.
- `HeuristicEvaluatorProvider`: local fallback provider for development and smoke tests.
- `build_evaluation_service`: creates the configured evaluator service.

### LLM

- `LLMRuntimeConfig`: local model settings.
- `LocalLlamaRuntime`: lazy cached `llama-cpp-python` runtime.
- `LocalLlamaEvaluatorProvider`: adapter from `LocalLlamaRuntime` to `EvaluatorProvider`.
- `OpenAIEvaluatorProvider`: adapter from the OpenAI Responses API to `EvaluatorProvider`.

### Configuration

- `EvaluatorConfig`: selected provider plus model-specific settings.
- `OpenAIModelConfig`: OpenAI model name and hyperparameters.
- `LocalLlamaModelConfig`: local model path and llama-cpp hyperparameters.
- `load_evaluator_config`: reads `config/evaluator_default.json` and environment overrides.

### Observability

- `log_timing`: prints consistent timing records for startup and evaluation latency.

### Transformation

- `TransformationPromptBuilder`: asks a stronger model to convert MCQ items into freeform recall prompts.
- `MultipleChoiceToFreeformTransformer`: applies the transformation to one or many source records.
- `OpenAITransformationProvider`: high-quality transformation provider for offline content generation.
- `HeuristicTransformationProvider`: local deterministic transformer for tests and smoke checks.

### Training

- `AnswerClassificationExample`: labeled learner answer for one question.
- `AnswerFeatureExtractor`: extracts answer/reference/provenance features.
- `ReinforcementAnswerClassifier`: trains a binary answer classifier with reward-based policy updates.
- `AnswerClassificationModel`: persisted classifier weights and threshold.
- `scripts/train_answer_classifier.py`: trains the classifier and fails if accuracy is below the required gate.

## Initial Implementation Notes

- The repository starts with `data/questions/sample_questions.json`, a random 10-question sample from the generated training question bank.
- Question artifacts preserve original multiple-choice source data under `original_multiple_choice`.
- `scripts/transform_questions.py` converts source MCQ JSON into transformed freeform JSON.
- `scripts/generate_sample_training_artifacts.py` creates the self-authored 100-question test bank and labeled answer examples used by the training gate.
- `scripts/generate_partial_answer_artifacts.py` creates training and holdout partial-credit datasets with continuous 0-to-1 answer ratings plus a coarse `rating_bucket` for provenance. It is intentionally kept out of the binary classifier training data until the scoring model is redesigned for partial credit.
- `scripts/select_sample_questions.py` refreshes the app sample file with 10 random questions from the generated training question bank. The script supports an optional `--seed` only for debugging a specific sample.
- The final verification set lives under `data/verification/` and must not be used by training scripts.
- `scripts/train_answer_classifier.py` must exceed the configured 90% held-out accuracy gate before any trained evaluator should be used in the app.
- V1 defaults to `HeuristicEvaluatorProvider` to keep development fast and deterministic.
- Local llama support remains available behind `LocalLlamaEvaluatorProvider`, but loading the model should be opt-in because it may download large model files.
- The default real evaluator model is `gpt-5.4-mini`, selected as a quality/cost/latency balance for structured answer evaluation. Use `gpt-5.5` when evaluation quality matters more than cost, and keep the heuristic provider for offline development.
- Evaluator provider, model name, and hyperparameters live in `config/evaluator_default.json` and can be overridden with environment variables.
- V1 ships with `provider: heuristic` so the app runs without an API key. Set `AWS_COACH_EVALUATOR_PROVIDER=openai` and `OPENAI_API_KEY` to use the OpenAI provider.
- The Streamlit entry point should remain thin and call package classes instead of embedding workflow logic directly in the UI.

## Acceptance Criteria

- Running the app shows at least one sample AWS question.
- Filters update the available question set.
- Submitting an answer produces a valid `EvaluationResult`.
- The session records completed questions and score history.
- The package modules compile with `python3 -m py_compile`.
