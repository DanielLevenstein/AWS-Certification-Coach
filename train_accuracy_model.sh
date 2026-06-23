#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

RELEASE_TAG=""
METRICS_DIR="metrics/$(date '+%Y%m%d_%H%M%S')"
case "${1:-}" in
  v[0-9]*.[0-9]*.[0-9]* | v[0-9]*.[0-9]*.[0-9]*.[0-9]*)
    RELEASE_TAG="$1"
    shift
    ;;
esac

.venv/bin/python scripts/combine_curated_training_data.py

.venv/bin/python scripts/train_answer_accuracy.py \
  --eval-mode training \
  --questions data/generated/questions_with_answers_training.json \
  --training-data data/generated/questions_with_answers_training.json \
  --validation-questions data/generated/questions_with_answers_validation.json \
  --validation-data data/generated/questions_with_answers_validation.json \
  --feedback-data data/curated/curated_training_data.json \
  --feedback-data data/generated/user_feedback.v2.json \
  --feedback-data data/generated/generated_feedback.json \
  --evaluation-data data/curated/curated_training_data.json \
  --evaluation-data data/generated/user_feedback.v2.json \
  --evaluation-data data/generated/generated_feedback.json \
  --output "$METRICS_DIR/answer_regressor_model.json" \
  --metrics-output "$METRICS_DIR/training_metrics.json" \
  --history-output "$METRICS_DIR/training_history.json" \
  "$@"

.venv/bin/python scripts/plot_training_history.py \
  --history "$METRICS_DIR/training_history.json" \
  --output "$METRICS_DIR/training_performance.png" \
  --accuracy-output "$METRICS_DIR/curated_grade_accuracy.png"

.venv/bin/python scripts/curated_failure_report.py \
  --model "$METRICS_DIR/answer_regressor_model.json" \
  --output "$METRICS_DIR/curated_failure_report.md"
.venv/bin/python scripts/evaluate_answer_model.py \
  --model "$METRICS_DIR/answer_regressor_model.json" \
  --json-output "$METRICS_DIR/answer_model_evaluation.json" \
  --table-output "$METRICS_DIR/answer_model_evaluation.md"
.venv/bin/python scripts/curated_rubric_review.py \
  --output "$METRICS_DIR/curated_rubric_review.md"
.venv/bin/python scripts/semantic_similarity_evaluation.py \
  --evaluation-data data/curated/curated_training_data.json \
  --evaluation-data data/generated/user_feedback.v2.json \
  --evaluation-data data/generated/generated_feedback.json \
  --output "$METRICS_DIR/semantic_similarity.json" \
  --chart-output "$METRICS_DIR/semantic_accuracy.png" \
  --per-grade-precision-output "$METRICS_DIR/per_grade_precision.png" \
  --answer-model-evaluation "$METRICS_DIR/answer_model_evaluation.json"
.venv/bin/python scripts/question_fidelity_evaluation.py \
  --output "$METRICS_DIR/question_fidelity.json"
.venv/bin/python scripts/release_metrics.py \
  --metrics-dir "$METRICS_DIR" \
  --output "$METRICS_DIR/summary.md"

if [ -n "$RELEASE_TAG" ]; then
  RELEASE_REPORT="release/release_${RELEASE_TAG}_release_report.md"
  mkdir -p release
  {
    printf '# Release %s Detailed Report\n\n' "$RELEASE_TAG"
    cat "$METRICS_DIR/summary.md"
    printf '\n'
    cat "$METRICS_DIR/curated_failure_report.md"
    printf '\n'
    cat "$METRICS_DIR/curated_rubric_review.md"
  } > "$RELEASE_REPORT"
  echo "Detailed release report: $RELEASE_REPORT"
fi

echo "Checkpoint data: $METRICS_DIR/training_history.json"
echo "Failure report: $METRICS_DIR/curated_failure_report.md"
echo "Preserved release artifacts: $METRICS_DIR"
