#!/usr/bin/env sh
set -e

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

echo "Running tests with pytest..."
.venv/bin/python -m pytest "$@"
