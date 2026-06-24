#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

case "${1:-}" in
  -h|--help)
    .venv/bin/python scripts/model_evaluation.py --help
    exit 0
    ;;
esac

.venv/bin/python test_suites.py model-training \
  --questions data/generated/questions_with_answers_training.json \
  --training-data data/generated/questions_with_answers_training.json \
  --evaluation-data data/curated/curated_training_data.json \
  "$@"
