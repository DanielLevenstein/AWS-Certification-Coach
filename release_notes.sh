#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

MODE="full"
if [ "$#" -gt 0 ]; then
  case "$1" in
    --full)
      MODE="full"
      shift
      ;;
    --quick)
      MODE="quick"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--full|--quick] <release-tag>" >&2
      echo "Example: $0 --full v2.2.0" >&2
      echo "Example: $0 --quick test-build" >&2
      exit 0
      ;;
  esac
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [--full|--quick] <release-tag>" >&2
  echo "Example: $0 --full v2.2.0" >&2
  echo "Example: $0 --quick test-build" >&2
  exit 2
fi

RELEASE_TAG="$1"
RELEASE_FILE_STEM="$(printf '%s' "$RELEASE_TAG" | tr -c '[:alnum:]._-' '_')"

if [ "$MODE" = "full" ]; then
  .venv/bin/python test_suites.py model
fi

METRICS_DIR="metrics/$(date '+%Y%m%d_%H%M%S')"
.venv/bin/python test_suites.py release \
  --release-label "$RELEASE_TAG" \
  --release-notes docs/RELEASE_NOTES.md \
  --metrics-dir "$METRICS_DIR"

ACCURACY_SOURCE="$METRICS_DIR/semantic_accuracy.png"
ACCURACY_OUTPUT="release/${RELEASE_FILE_STEM}_semantic_accuracy.png"
DOMAIN_COVERAGE_SOURCE="$METRICS_DIR/question_domain_coverage.png"
DOMAIN_COVERAGE_OUTPUT="release/${RELEASE_FILE_STEM}_question_domain_coverage.png"
INTENT_COVERAGE_SOURCE="$METRICS_DIR/question_intent_coverage.png"
INTENT_COVERAGE_OUTPUT="release/${RELEASE_FILE_STEM}_question_intent_coverage.png"
CERTIFICATION_COVERAGE_SOURCE="$METRICS_DIR/question_certification_coverage.png"
CERTIFICATION_COVERAGE_OUTPUT="release/${RELEASE_FILE_STEM}_question_certification_coverage.png"
LATEST_REPORT="$METRICS_DIR/curated_failure_report.md"
REPORT_OUTPUT="release/curated_failure_report.md"
mkdir -p release
cp -p "$ACCURACY_SOURCE" "$ACCURACY_OUTPUT"
cp -p "$DOMAIN_COVERAGE_SOURCE" "$DOMAIN_COVERAGE_OUTPUT"
cp -p "$INTENT_COVERAGE_SOURCE" "$INTENT_COVERAGE_OUTPUT"
cp -p "$CERTIFICATION_COVERAGE_SOURCE" "$CERTIFICATION_COVERAGE_OUTPUT"
cp -p "$LATEST_REPORT" "$REPORT_OUTPUT"
echo "Saved tagged accuracy chart: $ACCURACY_OUTPUT"
echo "Saved tagged domain coverage chart: $DOMAIN_COVERAGE_OUTPUT"
echo "Saved tagged question intent coverage chart: $INTENT_COVERAGE_OUTPUT"
echo "Saved tagged certification coverage chart: $CERTIFICATION_COVERAGE_OUTPUT"
echo "Saved latest release report $REPORT_OUTPUT"
