#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

case "${1:-}" in
  -h|--help)
    echo "Usage: $0 [pytest-options]"
    echo "Runs fast read-only model and knowledge contract tests without training."
    exit 0
    ;;
esac

.venv/bin/python test_suites.py model-smoke "$@"
