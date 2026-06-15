#!/usr/bin/env bash
set -euo pipefail

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python scripts/generate_sample_training_artifacts.py
.venv/bin/python scripts/generate_app_question_artifacts.py --count 80
