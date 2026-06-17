#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python test_suites.py model \
  --questions data/generated/questions_with_answers_training.json \
  --training-data data/generated/questions_with_answers_training.json \
  --evaluation-data data/curated/curated_training_data.json \
  --evaluation-data data/generated/user_feedback.v1.json \
  --evaluation-data data/generated/generated_feedback.json
