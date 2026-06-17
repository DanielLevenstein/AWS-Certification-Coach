#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

if [ "$#" -eq 0 ]; then
  .venv/bin/python scripts/generate_question_coverage.py
  exit 0
fi

case "$1" in
  -h|--help|--questions|--output|--chart-output)
    .venv/bin/python scripts/generate_question_coverage.py "$@"
    ;;
  -*)
    .venv/bin/python scripts/generate_question_coverage.py "$@"
    ;;
  *)
    if [ "$#" -ne 1 ]; then
      echo "Usage: $0 [release-tag] or $0 [generate_question_coverage.py options]" >&2
      echo "Example: $0 v2.2.0" >&2
      echo "Example: $0 --output release/metrics/question_coverage.json --chart-output release/metrics/question_coverage.png" >&2
      exit 2
    fi
    RELEASE_TAG="$1"
    RELEASE_FILE_STEM="$(printf '%s' "$RELEASE_TAG" | tr -c '[:alnum:]._-' '_')"
    mkdir -p release release/metrics
    .venv/bin/python scripts/generate_question_coverage.py \
      --output release/metrics/question_coverage.json \
      --chart-output "release/${RELEASE_FILE_STEM}_question_coverage.png"
    echo "Saved tagged question coverage chart: release/${RELEASE_FILE_STEM}_question_coverage.png"
    ;;
esac
