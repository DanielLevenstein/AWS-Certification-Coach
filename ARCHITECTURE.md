# AWS Certification Coach Architecture


## System Overview

```text
Student
  |
  v
Streamlit UI
  |
  v
Quiz Controller
  |
  +--> Question Repository
  |
  v
Evaluation Prompt Builder
  |
  v
Evaluation Service
  |
  v
Feedback Engine
  |
  v
Results Display
```

## Runtime Components

### Streamlit UI

The UI is responsible for the learner-facing workflow:

- Select certification, domain, and difficulty filters.
- Present one question at a time.
- Accept free-text learner responses.
- Display scores, missing concepts, recommended review topics, and a detailed correct answer.
- Show session progress and recent score history.

The UI should stay thin. It should delegate quiz state, question selection, prompt generation, model calls, and response formatting to application modules.

### Question Repository

The question repository stores reviewed certification practice content. The MVP can use JSON files because the app only needs read-heavy access to a curated question bank.

Example question shape:

```json
{
  "question_id": "AWS-001",
  "certification": "Cloud Practitioner",
  "domain": "Security",
  "difficulty": "Easy",
  "question": "What is the purpose of IAM roles?",
  "reference_answer": "IAM roles grant temporary permissions that AWS services, applications, or users can assume without long-lived credentials.",
  "key_concepts": [
    "IAM",
    "temporary credentials",
    "least privilege",
    "trusted entities"
  ]
}
```

Repository responsibilities:

- Load question files.
- Validate required fields.
- Filter by certification, domain, and difficulty.
- Support randomized quiz order.
- Preserve original multiple-choice source questions for post-answer review.
- Keep storage swappable for SQLite, PostgreSQL, or DynamoDB later.

### Quiz Controller

The quiz controller owns session behavior:

- Select the next question.
- Track completed question IDs.
- Track score history.
- Avoid repeating questions during a session.
- Maintain current filters and quiz mode.

Future versions can add adaptive difficulty, weak-area targeting, timed exam simulation, and persisted learner profiles.

### Evaluation Prompt Builder

The prompt builder converts a question, reference answer, key concepts, and learner answer into a consistent scoring request.

Prompt contract:

```text
Evaluate the learner's answer against the reference answer.

Question:
{question}

Reference answer:
{reference_answer}

Key concepts:
{key_concepts}

Learner answer:
{user_answer}

Return JSON only with:
- score: integer from 0 to 100
- missing_concepts: array of strings
- suggested_improvements: array of strings
- feedback: concise learner-facing explanation
- detailed_answer: detailed correct answer that covers the reference answer and every missing concept
```

The prompt builder should keep scoring instructions centralized so that every model provider receives the same evaluation contract.

### Evaluation Service

The evaluation service is the only runtime component that talks to the model provider. Runtime grading defaults to the trained classifier and can be switched to OpenAI through configuration, but the app should expose a narrow interface such as `evaluate_answer(prompt) -> EvaluationResult`.

Responsibilities:

- Load provider configuration.
- Reuse model clients across requests when possible.
- Apply deterministic generation settings for grading.
- Capture latency and provider errors.
- Return parseable JSON or a controlled error state.

### Feedback Engine

The feedback engine turns raw model output into the final learner display.

Responsibilities:

- Parse and validate model JSON.
- Normalize score values.
- Provide fallback feedback if the model returns malformed output.
- Format missed concepts, recommendations, and detailed answer guidance for the UI.

Example display content:

```text
Score: 85%

Areas to improve:
- Mention temporary credentials.
- Connect roles to least privilege.

Detailed answer:
Review IAM roles, trust policies, and temporary security credentials.
```

## Offline Content Generation

Practice questions are produced before deployment.

```text
AWS documentation and exam guide
  |
  v
Content generation script
  |
  v
Scripted self-authored generation
  |
  v
Human quality review
  |
  v
JSON question bank
```

Offline generation outputs:

- Combined question and answer files.
- Reference answers.
- Key concepts.
- Domain and difficulty metadata.
- Original multiple-choice provenance for transformed freeform questions.
- Binary, wrong-answer, and continuous partial-credit answer examples.

Keeping generation offline reduces runtime memory usage, startup time, and deployment complexity.

## Multiple-Choice to Freeform Transformation

V1 uses freeform learner prompts, but the source material should remain aligned with exam-style multiple-choice questions. The offline transformation pipeline converts licensed or self-authored multiple-choice questions into paragraph-answer prompts.

```text
Source multiple-choice artifact
  |
  v
Transformation prompt builder
  |
  v
High-quality LLM transformer
  |
  v
Freeform question artifact
  |
  +--> Original multiple-choice source preserved
```

The transformed artifact keeps the original multiple-choice question, answer choices, correct answer IDs, explanation, source name, source URL, and license notes. Generated training artifacts also keep answer examples in the same question row so human test cases can be added without synchronizing separate question and answer files. The app uses the transformed freeform prompt for recall practice, then displays the original multiple-choice item next to generated feedback after the learner submits an answer.

## Deployment

### Phase 1

```text
User
  |
  v
Streamlit App
  |
  v
Trained Classifier
```

Recommended targets:

- Render for a simple MVP.
- EC2 if local model hosting is required.
- A managed LLM API if startup time and small images are higher priority than fully local inference.

OpenAI remains available as an optional provider for model-based evaluation, but the default V1 deployment uses the trained local classifier and bundled model artifact.

Expected benefits:

- Smaller Docker image than the RAG prototype.
- Faster startup.
- Lower memory use.
- Fewer runtime artifacts to package.

### Phase 2

```text
User
  |
  v
CloudFront
  |
  v
Application Load Balancer
  |
  v
ECS/Fargate App
  |
  +--> DynamoDB
  |
  +--> Amazon Bedrock
```

Optional AWS services:

- CloudWatch for logs and metrics.
- S3 for question bank storage.
- Cognito for authentication.
- DynamoDB for learner progress.

## MVP Scope

Included:

- Question display.
- Free-text answer submission.
- LLM-based evaluation.
- Score generation.
- Feedback generation.
- Domain and difficulty filtering.
- Session progress tracking.

Excluded:

- Runtime RAG.
- FAISS.
- Embeddings.
- Document ingestion.
- User authentication.
- Multi-user persistence.

## Success Criteria

- Docker image under 1 GB when using a managed LLM provider.
- Startup under 30 seconds.
- Answer evaluation under 10 seconds for normal requests.
- Successful cloud deployment.
- At least 100 reviewed AWS certification questions.
- Evaluation responses are valid JSON at least 95% of the time in smoke tests.

## Reusable Code Candidates

The previous RAG prototype contains pieces worth carrying forward, even though the RAG-specific code should be left behind:

- Model configuration loading and overrides.
- Cached model/client lifecycle management.
- Timing helpers for cold start and request latency.
- Chat-completion wrapper for deterministic responses.
- Response trimming for local models that emit reasoning markers.

Do not carry forward:

- FAISS loading and querying.
- Sentence-transformer embedding setup.
- Pickled chunk loading.
- RAG-only prompts.
- Document chunking and ingestion.
