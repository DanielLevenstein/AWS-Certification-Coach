#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PYTHON_BIN=".venv/bin/python"
"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" scripts/recreate_mongo_database.py --drop-existing --yes "$@"
