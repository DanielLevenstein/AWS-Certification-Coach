#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

RELEASE_TAG=""
case "${1:-}" in
  v[0-9]*.[0-9]*.[0-9]* | v[0-9]*.[0-9]*.[0-9]*.[0-9]*)
    RELEASE_TAG="$1"
    shift
    ;;
esac

.venv/bin/python scripts/train_partial_answer_regressor.py \
  --eval-mode training \
  --output release/metrics/partial_answer_regressor.json \
  --metrics-output release/metrics/training_metrics.json \
  --history-output release/metrics/training_history.json \
  "$@"

.venv/bin/python scripts/plot_training_history.py \
  --history release/metrics/training_history.json \
  --output release/metrics/training_performance.png \
  --accuracy-output release/metrics/curated_grade_accuracy.png

.venv/bin/python scripts/curated_failure_report.py
.venv/bin/python scripts/semantic_similarity_evaluation.py
.venv/bin/python scripts/release_metrics.py

CHART_RUN_DIR="data/charts/$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$CHART_RUN_DIR"
cp -p \
  release/metrics/training_performance.png \
  release/metrics/curated_grade_accuracy.png \
  release/metrics/training_history.json \
  release/metrics/training_metrics.json \
  release/metrics/partial_answer_regressor.json \
  release/metrics/curated_failure_report.md \
  release/metrics/semantic_similarity.json \
  release/metrics/summary.md \
  "$CHART_RUN_DIR/"

if [ -n "$RELEASE_TAG" ]; then
  RELEASE_REPORT="release/release_${RELEASE_TAG}_release_report.md"
  mkdir -p release
  {
    printf '# Release %s Detailed Report\n\n' "$RELEASE_TAG"
    cat release/metrics/summary.md
    printf '\n'
    cat release/metrics/curated_failure_report.md
  } > "$RELEASE_REPORT"
  echo "Detailed release report: $RELEASE_REPORT"
fi

echo "Checkpoint data: release/metrics/training_history.json"
echo "Failure report: release/metrics/curated_failure_report.md"
echo "Preserved release artifacts: $CHART_RUN_DIR"
