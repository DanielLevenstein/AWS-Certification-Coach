#!/usr/bin/env sh
set -e

# Activate a local virtualenv if present
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
elif [ -f venv/bin/activate ]; then
  . venv/bin/activate
fi

# Attempt to run available metrics generator
if [ -f scripts/release_metrics.py ]; then
  python scripts/release_metrics.py "$@"
else
  echo "No metrics generator found at scripts/release_metrics.py"
  exit 1
fi
