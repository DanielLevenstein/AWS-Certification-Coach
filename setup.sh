#!/usr/bin/env bash
set -euo pipefail

# Ensure local src is on the import path for scripts
export PYTHONPATH=src

python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80

python -m pip install -r requirements.txt
python -m pytest
python scripts/release_metrics.py

