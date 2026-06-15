#!/usr/bin/env bash
set -euo pipefail

# Ensure local src is on the import path for scripts
export PYTHONPATH=src

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PYTHON_BIN=".venv/bin/python"

# Ensure the directory exists
mkdir -p data/curated

"$PYTHON_BIN" scripts/combine_curated_training_data.py

"$PYTHON_BIN" -m pip install -r requirements.txt

"$PYTHON_BIN" scripts/generate_sample_training_artifacts.py
"$PYTHON_BIN" scripts/generate_app_question_artifacts.py --count 80
