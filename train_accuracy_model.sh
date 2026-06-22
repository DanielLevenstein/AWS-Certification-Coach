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

if [ ! -f models/huggingface/all-MiniLM-L6-v2/model.safetensors ]; then
  .venv/bin/python scripts/download_answer_embedding_model.py
fi

.venv/bin/python scripts/train_semantic_answer_classifier.py \
  --metrics-output "$METRICS_DIR/semantic_classifier_training.json"
.venv/bin/python scripts/evaluate_semantic_answer_classifier.py \
  --output "$METRICS_DIR/semantic_classifier_test.json" \
  --chart-output "$METRICS_DIR/semantic_accuracy.png" \
  --per-grade-precision-chart-output "$METRICS_DIR/per_grade_precision.png"
.venv/bin/python scripts/compare_answer_evaluators.py \
  --device cpu \
  --output "$METRICS_DIR/answer_evaluator_comparison.json"

.venv/bin/python scripts/curated_failure_report.py \
  --output "$METRICS_DIR/curated_failure_report.md"
.venv/bin/python scripts/curated_rubric_review.py \
  --output "$METRICS_DIR/curated_rubric_review.md"
.venv/bin/python scripts/semantic_similarity_evaluation.py \
  --evaluation-data data/curated/curated_training_data.json \
  --evaluation-data data/generated/user_feedback.v2.json \
  --evaluation-data data/generated/generated_feedback.json \
  --output "$METRICS_DIR/semantic_similarity.json" \
  --chart-output "$METRICS_DIR/legacy_semantic_accuracy.png" \
  "$@"
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

echo "Production scoring calibration and evaluation completed (no regressor training)."
echo "Failure report: $METRICS_DIR/curated_failure_report.md"
echo "Preserved release artifacts: $METRICS_DIR"
