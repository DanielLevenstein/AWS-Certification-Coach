#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python test_suites.py model \
  --questions data/generated/questions_with_answers_test.json \
  --training-data data/generated/questions_with_answers_test.json
