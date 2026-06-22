# AWS Certification Coach

AI study partner for AWS certification exams.

<img src="docs/images/question_certification_coverage.png" alt="Certification Exam Split" width="720">

*Figure: Shows test exam breakdown for project.*

  
## Live Demo

The latest version of this project is deployed live on Render.
- v1 Deployment: [AWS Certification Coach](https://aws-certification-coach-latest.onrender.com/)

## Application Screenshot

<img src="docs/images/aws-certification-coach2.png" alt="Certification Exam Screenshot" width="720">

*Figure: The coach scores a freeform Amazon Kinesis answer and displays detailed feedback alongside the source multiple-choice question.*

## Goal

AWS Certification Coach is a lightweight study app for AWS certification practice. It presents pre-generated freeform questions, evaluates learner answers with a local SentenceTransformer encoder and supervised A/B/C/D/F classifier, and returns structured coaching feedback.

Version 3 has no runtime RAG stack, document ingestion, FAISS index, vector database, or hosted grading API. Certification content is generated and reviewed offline. A pinned local embedding model normalizes learner answers before a small supervised classifier assigns the grade.

The v3 contracts are documented in:

- `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_DESIGN.md`
- `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_ARCHITECTURE.md`
- `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_METRICS.md`

## Training Data Generation

The V1 training data is generated offline from self-authored, exam-style AWS scenarios. The project does not copy real exam dumps, paid practice-test text, or restricted AWS Skill Builder content. AWS exam guides and documentation are used as style and scope references, while the local artifacts are generated specifically for this project.

The generation flow starts with service-level scenario specs in `scripts/generate_sample_training_artifacts.py`. Each spec defines the target AWS service or feature, certification, domain, difficulty, expected purpose, key concepts, and plausible distractors. The script turns those specs into original multiple-choice questions, then converts them into freeform recall prompts so learners must explain the answer instead of recognizing it from choices.

Each generated question keeps its source-style multiple-choice item in the same JSON row under `original_multiple_choice`. The same row also stores answer examples used for diagnostic model training:

- `generated_answers`: complete, partial, weak, and incorrect answers labeled with human-readable grades `A`, `B`, `C`, `D`, and `F`, plus `intended_coverage` metadata.

Training, validation, and final-test data are generated separately. `config/data/structured_answer_training_data.json` may augment training only. Final-test rows are never used for fitting, feature selection, thresholds, or runtime calibration.

Artifacts keep letter grades for readability. Migration metrics preserve the historical grade bands `A/B`, `C/D`, and `F`; within-one-letter accuracy above 90% is the v3 release gate, while exact-letter accuracy remains an honestly reported diagnostic.

To regenerate local data:

```bash
./setup.sh
```

## Releases

| Release | Description                                                                                        |
|---------|----------------------------------------------------------------------------------------------------|
| v1.0.0  | Initial Streamlit/Docker release with generated AWS certification practice questions..             |
| v1.1.0  | Separated the app-facing question bank from training labels.                                       |
| v1.3.1  | Test framework redesign; initial curated grade-band accuracy was 44%.                              |
| v1.3.4  | Swapped default app scoring to`semantic_similarity`; curated grade-band accuracy reached 80%.      |
| v1.5.3  | Updated test data to have proper train, test, validation split                                     |
| v1.5.4  | Made`semantic_similarity` the official model name, moved release gating to 80% semantic precision. |
| v2.1.1  | Added AWS Developer Certification practice questions                                               |
| v2.3.6  | Improved answer evaluation model and added within one letter grade metric to release notes         |
| v2.4.5  | Got exact letter accuracy metric over 87%                                                          |
#### Scope

Certifications:

- Cloud Practitioner
- Solutions Architect Associate
- AWS Developer Exam 

Difficulty:

- Easy
- Medium

## Previous Application

This project was inspired by my previous AWS Documentation RAG project.

- v0 GitHub:  [DanielLevenstein/AWS-Documentation-Rag](https://github.com/DanielLevenstein/AWS-Documentation-Rag)


## Setup

Create the virtual environment, install dependencies, and generate local data:

```bash
./setup.sh
```

Download the pinned local encoder and train the classifier candidate:

```bash
.venv/bin/python scripts/download_answer_embedding_model.py
./train_accuracy_model.sh
```

Then run the app:

```bash
./run_app.sh
```

Run the fast unit and contract tests:

```bash
./run_unit_tests.sh
```

Run model-quality checks separately:

```bash
./run_model_tests.sh
```

Answer grading runs locally with `sentence-transformers/all-MiniLM-L6-v2`. Download it before starting or building the app:

```bash
.venv/bin/python scripts/download_answer_embedding_model.py
```

The default device mode is `auto`, allowing SentenceTransformers to use an available accelerator and falling back to CPU. The Docker production image sets `AWS_COACH_CPU_ONLY=1` to force CPU inference. A supervised A/B/C/D/F classification head is trained over normalized learner/reference embedding features; `config/data/structured_answer_training_data.json` augments only the training split. Run `./train_accuracy_model.sh` to train against training plus structured rows, select against validation, and report the untouched final test split.

Run the release suite and save the latest release chart artifacts:

```bash
./release_notes.sh --quick v2.2.0
```

The release helper saves answer-classifier metrics, the legacy migration comparison, question-fidelity results, question-coverage charts, and a combined release report under `metrics/<timestamp>/`.

Run the complete tagged release report:

```bash
./release_notes.sh --full v2.2.0
```

Generated metrics and charts are written under `metrics/<timestamp>/` and are not committed. Release notes retain historical values and add a versioned v3 migration table produced by running the legacy and candidate evaluators against the same frozen benchmark.

Regenerate local training, validation, test, and app sample artifacts:

```bash
.venv/bin/python scripts/generate_sample_training_artifacts.py
.venv/bin/python scripts/generate_app_question_artifacts.py --count 80
```

Train the semantic classifier, validate it, and produce final-test diagnostics:

```bash
./train_accuracy_model.sh
```

The script fits only against training plus approved structured examples, selects against validation, and evaluates the frozen final test only for release reporting. It does not create runtime question-and-answer calibration lookups.

Print a single release-note-friendly model performance summary:

```bash
.venv/bin/python scripts/release_metrics.py
```

Final verification data is stored separately in `data/generated/questions_with_answers_test.json`. Do not use that file for training.

## Docker

Build the container image:

```bash
docker build -t aws-certification-coach:latest .
```

Run the app on port 8501:

```bash
docker run --rm -p 8501:8501 aws-certification-coach:latest
```

The image includes reviewed questions, the pinned local encoder, the versioned classifier artifact, and local scoring code. Runtime grading is fully local and requires no network access.

## Render Deployment

- Runtime: Docker
- Port: use Render's `PORT` environment variable; the container defaults to `8501` for local runs.
- Health check path: `/_stcore/health`
- Default evaluator: local SentenceTransformer semantic classifier
- API key requirement: none for the default local path.
- Device: CPU-only in the production Docker image.

## Evaluator Configuration

The v3 evaluator converts learner answers and rubric evidence into normalized semantic relationship features, then predicts A/B/C/D/F with a supervised classifier. The legacy `semantic_similarity` evaluator remains available only for migration comparison and rollback testing.
