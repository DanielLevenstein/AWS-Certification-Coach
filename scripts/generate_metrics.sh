#!/usr/bin/env sh
set -e

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

# Attempt to run available metrics generator
if [ -f scripts/release_metrics.py ]; then
  .venv/bin/python scripts/release_metrics.py "$@"
else
  echo "No metrics generator found at scripts/release_metrics.py"
  exit 1
fi
