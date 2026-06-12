#!/usr/bin/env bash
# Helper script to run model training pipeline
# Usage: ./train.sh [options]

set -euo pipefail

cd "$(dirname "$0")"
python scripts/run_training_pipeline.py "$@"
