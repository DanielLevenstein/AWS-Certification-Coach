#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

rm -rf data
rm -rf metrics
rm -rf scripts/data