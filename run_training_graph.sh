#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

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

CHART_RUN_DIR="data/charts/$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$CHART_RUN_DIR"
cp -p \
  release/metrics/training_performance.png \
  release/metrics/curated_grade_accuracy.png \
  release/metrics/training_history.json \
  release/metrics/training_metrics.json \
  release/metrics/partial_answer_regressor.json \
  release/metrics/curated_failure_report.md \
  "$CHART_RUN_DIR/"

echo "Checkpoint data: release/metrics/training_history.json"
echo "Failure report: release/metrics/curated_failure_report.md"
echo "Preserved release artifacts: $CHART_RUN_DIR"
