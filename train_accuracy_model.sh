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

.venv/bin/python scripts/train_answer_accuracy.py \
  --eval-mode training \
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
.venv/bin/python scripts/semantic_similarity_evaluation.py \
  --output "$METRICS_DIR/semantic_similarity.json" \
  --chart-output "$METRICS_DIR/semantic_accuracy.png"
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
  } > "$RELEASE_REPORT"
  echo "Detailed release report: $RELEASE_REPORT"
fi

echo "Checkpoint data: $METRICS_DIR/training_history.json"
echo "Failure report: $METRICS_DIR/curated_failure_report.md"
echo "Preserved release artifacts: $METRICS_DIR"
