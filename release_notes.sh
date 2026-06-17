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
COVERAGE_SOURCE="$METRICS_DIR/question_coverage.png"
COVERAGE_OUTPUT="release/${RELEASE_FILE_STEM}_question_coverage.png"
LATEST_REPORT="$METRICS_DIR/curated_failure_report.md"
REPORT_OUTPUT="release/curated_failure_report.md"
mkdir -p release
cp -p "$ACCURACY_SOURCE" "$ACCURACY_OUTPUT"
cp -p "$COVERAGE_SOURCE" "$COVERAGE_OUTPUT"
cp -p "$LATEST_REPORT" "$REPORT_OUTPUT"
echo "Saved tagged accuracy chart: $ACCURACY_OUTPUT"
echo "Saved tagged question coverage chart: $COVERAGE_OUTPUT"
echo "Saved latest release report $REPORT_OUTPUT"
