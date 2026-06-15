#!/usr/bin/env bash
set -euo pipefail

python3 scripts/generate_sample_training_artifacts.py
python3 scripts/generate_app_question_artifacts.py --count 80
