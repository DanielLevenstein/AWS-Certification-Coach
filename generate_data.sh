#!/usr/bin/env bash
set -euo pipefail

python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80
