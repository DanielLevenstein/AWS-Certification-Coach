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
  -h|--help|--questions|--output|--chart-output|--chart-output-dir)
    .venv/bin/python scripts/generate_question_coverage.py "$@"
    ;;
  -*)
    .venv/bin/python scripts/generate_question_coverage.py "$@"
    ;;
  *)
    if [ "$#" -ne 1 ]; then
      echo "Usage: $0 [release-tag] or $0 [generate_question_coverage.py options]" >&2
      echo "Example: $0 v2.2.0" >&2
      echo "Example: $0 --output release/metrics/question_coverage.json --chart-output-dir release/metrics" >&2
      exit 2
    fi
    mkdir -p release release/metrics
    .venv/bin/python scripts/generate_question_coverage.py \
      --output release/metrics/question_coverage.json \
      --chart-output-dir release/metrics
    cp -p release/metrics/question_domain_coverage.png "release/question_domain_coverage.png"
    cp -p release/metrics/question_intent_coverage.png "release/question_intent_coverage.png"
    cp -p release/metrics/question_certification_coverage.png "release/question_certification_coverage.png"
    echo "Saved latest domain coverage chart: release/question_domain_coverage.png"
    echo "Saved latest question intent coverage chart: release/question_intent_coverage.png"
    echo "Saved latest certification coverage chart: release/question_certification_coverage.png"
    ;;
esac
