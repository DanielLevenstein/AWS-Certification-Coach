#!/usr/bin/env sh
set -e

# Activate a local virtualenv if present
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
elif [ -f venv/bin/activate ]; then
  . venv/bin/activate
fi

echo "Running tests with pytest..."
pytest "$@"
