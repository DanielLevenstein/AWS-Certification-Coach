#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

case "${1:-}" in
  -h|--help)
    echo "Usage: DOCKER_IMAGE=<image> $0 [pytest-options]"
    echo "Runs deployment tests against an already-built Docker image."
    exit 0
    ;;
esac

if [ -z "${DOCKER_IMAGE:-}" ]; then
  echo "DOCKER_IMAGE must name the already-built image to test." >&2
  exit 2
fi

.venv/bin/python test_suites.py deployment "$@"
