# Model Training Scripts

Helper scripts for orchestrating the AWS Certification Coach model training pipeline.

## Data Management

The training pipeline automatically manages training data:

- **Source data** (`config/curated_training_data.json`, `config/user_feedback.v1.json`) are stored in `config/` and committed to source control
- **Working data** are copied to `data/curated/` at pipeline startup (not committed)
- **Generated data** (`data/generated/`) are produced by generation scripts (not committed)
- **Models** (`models/`) are trained artifacts (not committed)

The pipeline copies config files to `data/curated/` before training automatically, so training scripts always read from `data/curated/`.

### .gitignore Configuration

The following directories are excluded from source control:
```
data/generated/     # Generated training data
data/curated/       # Working copy of curated training data  
models/             # Trained model files
```

### Run complete training pipeline:
```bash
./scripts/train.sh
# or
python scripts/run_training_pipeline.py
```

### Run specific models:
```bash
# Train only the answer classifier
./scripts/train.sh --classifier-only

# Train only the partial-credit regressor
./scripts/train.sh --regressor-only
```

### Skip certain steps:
```bash
# Skip data generation (use existing data)
./scripts/train.sh --skip-generation

# Skip question transformation
./scripts/train.sh --skip-transform

# Skip both data generation and transformation
./scripts/train.sh --skip-generation --skip-transform
```

### Debug and monitoring:
```bash
# Verbose output for detailed debugging
./scripts/train.sh --verbose

# Use training set evaluation (instead of leave-one-question-out)
./scripts/train.sh --eval-mode training
```

## Pipeline Stages

The training pipeline orchestrates four main stages:

### 1. **Data Generation** (optional)
Generates training data from raw question sources:
- `scripts/generate_sample_training_artifacts.py` - Creates sample training artifacts
- `scripts/generate_app_question_artifacts.py` - Generates app-facing question artifacts

**Skip with:** `--skip-generation`

### 2. **Question Transformation** (optional)
Converts multiple-choice questions to freeform format for training:
- `scripts/transform_questions.py` - Transforms MCQ → freeform

**Skip with:** `--skip-transform`

### 3. **Answer Classifier Training**
Trains binary answer classification model with reinforcement learning:
- Input: `data/generated/questions_with_answers_generated.json`
- Output: `models/answer_classifier.json`, `models/answer_classifier_metrics.json`
- Evaluates classification accuracy with leave-one-question-out cross-validation
- Fails if accuracy is below 90% or suspiciously high (>99.9%)

**Skip with:** `--classifier-only` (when using `--regressor-only`)

### 4. **Partial-Credit Regressor Training**
Trains continuous partial-credit scoring model:
- Input: `data/generated/questions_with_answers_generated.json`
- Output: `models/partial_answer_regressor.json`, `models/partial_answer_regressor_metrics.json`
- Evaluates with Mean Squared Error (MSE)
- Requires minimum 100 training examples

**Skip with:** `--regressor-only` (when using `--classifier-only`)

## Evaluation Modes

### Leave-One-Question-Out (default)
```bash
./scripts/train.sh --eval-mode leave-one-question-out
```
More rigorous cross-validation: trains on all-but-one questions, tests on held-out question.

### Training Set
```bash
./scripts/train.sh --eval-mode training
```
Faster evaluation using training set (less rigorous but useful for iteration).

## Advanced Usage

### Combine options:
```bash
# Train regressor only with verbose output using training set evaluation
./scripts/train.sh --regressor-only --verbose --eval-mode training

# Skip generation, train classifier only, with verbose output
./scripts/train.sh --skip-generation --classifier-only --verbose
```

## Output

The pipeline produces:

**Classifier Model:**
- `models/answer_classifier.json` - Trained classifier weights and threshold
- `models/answer_classifier_metrics.json` - Accuracy, precision, recall, F1 scores

**Regressor Model:**
- `models/partial_answer_regressor.json` - Trained regressor weights
- `models/partial_answer_regressor_metrics.json` - MSE, MAE, and other regression metrics

**Generated Data:**
- `data/generated/questions_with_answers_generated.json` - Generated training questions
- `data/generated/questions_transformed.json` - Transformed questions (if transformation runs)

## Troubleshooting

### Pipeline fails with "file not found"
Check that source config files exist:
```bash
ls config/curated_training_data.json
ls config/user_feedback.v1.json
```

The pipeline automatically copies these to `data/curated/` before training. If the config files don't exist, training will fail.

### Classifier accuracy too low
- Ensure sufficient training examples (minimum 50 required)
- Check data quality in `data/curated/` files
- Review feedback data in `config/` directory

### Memory issues
Run models individually to reduce memory pressure:
```bash
./scripts/train.sh --classifier-only
./scripts/train.sh --skip-generation --regressor-only
```

## Implementation Details

See [DESIGN.md](../DESIGN.md) for comprehensive documentation of:
- `ReinforcementAnswerClassifier` - Binary classification with reward-based policy
- `PartialCreditRegressor` - Continuous partial-credit scoring
- Feature extraction and model evaluation metrics
