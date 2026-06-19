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

AWS Certification Coach is a lightweight study app for AWS certification practice. It presents pre-generated freeform questions, evaluates learner answers with the local `semantic_similarity` model by default, and returns structured coaching feedback.

This version intentionally removes the runtime RAG stack from the earlier prototype. There is no document ingestion, FAISS index, vector database, or embedding model in the deployed app. Certification content is generated and reviewed offline, then served from a simple question repository.

## Training Data Generation

The V1 training data is generated offline from self-authored, exam-style AWS scenarios. The project does not copy real exam dumps, paid practice-test text, or restricted AWS Skill Builder content. AWS exam guides and documentation are used as style and scope references, while the local artifacts are generated specifically for this project.

The generation flow starts with service-level scenario specs in `scripts/generate_sample_training_artifacts.py`. Each spec defines the target AWS service or feature, certification, domain, difficulty, expected purpose, key concepts, and plausible distractors. The script turns those specs into original multiple-choice questions, then converts them into freeform recall prompts so learners must explain the answer instead of recognizing it from choices.

Each generated question keeps its source-style multiple-choice item in the same JSON row under `original_multiple_choice`. The same row also stores answer examples used for diagnostic model training:

- `generated_answers`: complete, partial, weak, and incorrect answers labeled with human-readable grades `A`, `B`, `C`, `D`, and `F`, plus `intended_coverage` metadata.

Training and verification data are generated separately:

Artifacts keep letter grades for readability. Curated release metrics compare the three grade bands `A/B`, `C/D`, and `F`. Precision and recall treat `A/B` and `C/D` as accepted answers and `F` as rejected.

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

Run the release suite and save the latest release chart artifacts:

```bash
./release_notes.sh --quick v2.2.0
```

The release helper saves the `semantic_similarity` diagnostic chart, separate question coverage charts for domain, intent, and certification split, and a combined four-panel chart as latest-only files in `release/`.

Refresh the training graph, curated failure report, semantic metrics, and detailed tagged report:

```bash
./release_notes.sh --full v2.2.0
```

The pandas/Matplotlib graphs are written to a timestamped root-level `metrics/<timestamp>/` directory along with `semantic_accuracy.png`, the question coverage PNGs, `semantic_similarity.json`, `summary.md`, the trained model checkpoint, and the curated failure report. Detailed failing questions, label conflicts, and suspected causes are written to `metrics/<timestamp>/curated_failure_report.md`. The release helper publishes latest-only individual chart files at `release/semantic_accuracy.png`, `release/question_domain_coverage.png`, `release/question_intent_coverage.png`, and `release/question_certification_coverage.png`. The only versioned chart artifact is the combined `release/release_metrics_chart.png`, plus the markdown reports in `release/`.

Regenerate local training, validation, test, and app sample artifacts:

```bash
.venv/bin/python scripts/generate_sample_training_artifacts.py
.venv/bin/python scripts/generate_app_question_artifacts.py --count 80
```

Train the diagnostic partial-credit regressor:

```bash
.venv/bin/python scripts/train_answer_accuracy.py
```

The regression metrics are retained for diagnostics, but release tracking uses `semantic_similarity` precision as the guardrail.

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

The image includes generated sample questions and local scoring code. The default app path is fully local.

## Render Deployment

- Runtime: Docker
- Port: use Render's `PORT` environment variable; the container defaults to `8501` for local runs.
- Health check path: `/_stcore/health`
- Default evaluator: local `semantic_similarity` scoring
- API key requirement: none for the default local path.

## Evaluator Configuration

The `semantic_similarity` scorer recognizes canonical service aliases, concept coverage, incorrect answer choices, and simple answer/reference overlap. 
