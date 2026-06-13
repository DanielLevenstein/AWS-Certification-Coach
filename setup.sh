#!/usr/bin/env bash
set -euo pipefail

# Ensure local src is on the import path for scripts
export PYTHONPATH=src

# Ensure the directory exists
mkdir -p data/curated

cp -f config/curated_training_data.json data/curated/curated_training_data.json

python -m pip install -r requirements.txt

python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80

python -m pytest
python scripts/release_metrics.py

