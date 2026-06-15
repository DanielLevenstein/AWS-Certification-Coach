
#!/bin/bash

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

#!/usr/bin/env bash
# Helper script to run model training pipeline
# Usage: ./train.sh [options]

set -euo pipefail

cd "$(dirname "$0")"
python scripts/run_training_pipeline.py "$@"
