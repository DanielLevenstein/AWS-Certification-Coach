#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python test_suites.py model \
  --evaluation-data data/curated/curated_training_data.json

.venv/bin/python scripts/evaluate_semantic_answer_classifier.py \
  --device cpu \
  --output metrics/semantic_classifier_test.json

.venv/bin/python scripts/compare_answer_evaluators.py \
  --device cpu \
  --output metrics/answer_evaluator_comparison.json
