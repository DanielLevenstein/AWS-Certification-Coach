#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

MODE="full"
STRICT_GRADING=0
if [ "$#" -gt 0 ]; then
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --full)
        MODE="full"
        shift
        ;;
      --quick)
        MODE="quick"
        shift
        ;;
      --strict-grading)
        STRICT_GRADING=1
        shift
        ;;
      -h|--help)
        echo "Usage: $0 [--full|--quick] [--strict-grading] <release-tag>" >&2
        echo "Example: $0 --full --strict-grading v2.3.1" >&2
        echo "Example: $0 --quick test-build" >&2
        exit 0
        ;;
      *)
        break
        ;;
    esac
  done
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 [--full|--quick] [--strict-grading] <release-tag>" >&2
  echo "Example: $0 --full --strict-grading v2.3.1" >&2
  echo "Example: $0 --quick test-build" >&2
  exit 2
fi

RELEASE_TAG="$1"
TEST_STATUS=0

if [ "$MODE" = "full" ]; then
  if ! .venv/bin/python test_suites.py unit; then
    echo "Unit tests failed; continuing so release metrics can still be generated." >&2
    TEST_STATUS=1
  fi
  if ! .venv/bin/python test_suites.py model-smoke; then
    echo "Model smoke tests failed; continuing so release metrics can still be generated." >&2
    TEST_STATUS=1
  fi
  METRICS_DIR="metrics/$(date '+%Y%m%d_%H%M%S')"
  RELEASE_SUITE="release"
else
  METRICS_DIR="${RELEASE_METRICS_DIR:-}"
  if [ -z "$METRICS_DIR" ]; then
    LATEST_SEMANTIC_METRICS="$(find metrics -mindepth 2 -maxdepth 2 -name semantic_similarity.json -print 2>/dev/null | sort | tail -n 1)"
    if [ -z "$LATEST_SEMANTIC_METRICS" ]; then
      echo "Quick release requires a previous full metrics run." >&2
      echo "Run ./release_notes.sh --full <tag> first or set RELEASE_METRICS_DIR." >&2
      exit 2
    fi
    METRICS_DIR="$(dirname "$LATEST_SEMANTIC_METRICS")"
  fi
  RELEASE_SUITE="release-quick"
fi

if [ "$TEST_STATUS" -ne 0 ]; then
  echo "Pre-release tests failed; generating metrics summary without updating release notes." >&2
  if [ "$STRICT_GRADING" = "1" ]; then
    .venv/bin/python test_suites.py "$RELEASE_SUITE" \
      --release-label "$RELEASE_TAG" \
      --metrics-dir "$METRICS_DIR" \
      --strict-grading \
      --summary-only
  else
    .venv/bin/python test_suites.py "$RELEASE_SUITE" \
      --release-label "$RELEASE_TAG" \
      --metrics-dir "$METRICS_DIR" \
      --summary-only
  fi
  echo "Release metrics directory: $METRICS_DIR" >&2
  echo "Release metrics were generated, but one or more pre-release test suites failed." >&2
  exit "$TEST_STATUS"
fi

RELEASE_STATUS=0
if [ "$STRICT_GRADING" = "1" ]; then
  .venv/bin/python test_suites.py "$RELEASE_SUITE" \
    --release-label "$RELEASE_TAG" \
    --release-notes RELEASE_NOTES.md \
    --metrics-dir "$METRICS_DIR" \
    --strict-grading || RELEASE_STATUS=$?
else
  .venv/bin/python test_suites.py "$RELEASE_SUITE" \
    --release-label "$RELEASE_TAG" \
    --release-notes RELEASE_NOTES.md \
    --metrics-dir "$METRICS_DIR" || RELEASE_STATUS=$?
fi

if [ "$RELEASE_STATUS" -ne 0 ]; then
  echo "Release metrics failed; rerunning summary-only metrics without updating release notes." >&2
  if [ "$STRICT_GRADING" = "1" ]; then
    .venv/bin/python test_suites.py release-quick \
      --release-label "$RELEASE_TAG" \
      --metrics-dir "$METRICS_DIR" \
      --strict-grading \
      --summary-only
  else
    .venv/bin/python test_suites.py release-quick \
      --release-label "$RELEASE_TAG" \
      --metrics-dir "$METRICS_DIR" \
      --summary-only
  fi
  echo "Release metrics directory: $METRICS_DIR" >&2
  exit "$RELEASE_STATUS"
fi

PER_GRADE_SOURCE="$METRICS_DIR/per_grade_metrics.png"
PER_GRADE_OUTPUT="release/per_grade_metrics.png"
GRADE_BAND_SOURCE="$METRICS_DIR/grade_band_metrics.png"
GRADE_BAND_OUTPUT="release/grade_band_metrics.png"
SEMANTIC_ACCURACY_SOURCE="$METRICS_DIR/semantic_accuracy.png"
SEMANTIC_ACCURACY_OUTPUT="release/semantic_accuracy.png"
DOMAIN_COVERAGE_SOURCE="$METRICS_DIR/question_domain_coverage.png"
DOMAIN_COVERAGE_OUTPUT="release/question_domain_coverage.png"
INTENT_COVERAGE_SOURCE="$METRICS_DIR/question_intent_coverage.png"
INTENT_COVERAGE_OUTPUT="release/question_intent_coverage.png"
CERTIFICATION_COVERAGE_SOURCE="$METRICS_DIR/question_certification_coverage.png"
CERTIFICATION_COVERAGE_OUTPUT="release/question_certification_coverage.png"
ACCURACY_CHART_OUTPUT="release/accuracy_metrics_chart.png"
QUESTION_COVERAGE_CHART_OUTPUT="release/question_coverage_metrics_chart.png"
LATEST_REPORT="$METRICS_DIR/curated_failure_report.md"
REPORT_OUTPUT="release/curated_failure_report.md"
LATEST_RUBRIC_REVIEW="$METRICS_DIR/curated_rubric_review.md"
RUBRIC_REVIEW_OUTPUT="release/curated_rubric_review.md"
mkdir -p release
cp -p "$PER_GRADE_SOURCE" "$PER_GRADE_OUTPUT"
cp -p "$GRADE_BAND_SOURCE" "$GRADE_BAND_OUTPUT"
cp -p "$SEMANTIC_ACCURACY_SOURCE" "$SEMANTIC_ACCURACY_OUTPUT"
cp -p "$DOMAIN_COVERAGE_SOURCE" "$DOMAIN_COVERAGE_OUTPUT"
cp -p "$INTENT_COVERAGE_SOURCE" "$INTENT_COVERAGE_OUTPUT"
cp -p "$CERTIFICATION_COVERAGE_SOURCE" "$CERTIFICATION_COVERAGE_OUTPUT"
cp -p "$LATEST_REPORT" "$REPORT_OUTPUT"
cp -p "$LATEST_RUBRIC_REVIEW" "$RUBRIC_REVIEW_OUTPUT"
.venv/bin/python scripts/combine_release_charts.py \
  --semantic-accuracy "$SEMANTIC_ACCURACY_SOURCE" \
  --per-grade "$PER_GRADE_SOURCE" \
  --grade-bands "$GRADE_BAND_SOURCE" \
  --domain-coverage "$DOMAIN_COVERAGE_SOURCE" \
  --intent-coverage "$INTENT_COVERAGE_SOURCE" \
  --certification-coverage "$CERTIFICATION_COVERAGE_SOURCE" \
  --accuracy-output "$ACCURACY_CHART_OUTPUT" \
  --coverage-output "$QUESTION_COVERAGE_CHART_OUTPUT"
cp -p "$ACCURACY_CHART_OUTPUT" "release/${RELEASE_TAG}"_accuracy_metrics_chart.png

echo "Saved latest per-grade precision and recall chart: $PER_GRADE_OUTPUT"
echo "Saved latest grade-band chart: $GRADE_BAND_OUTPUT"
echo "Saved latest semantic similarity chart: $SEMANTIC_ACCURACY_OUTPUT"
echo "Saved latest domain coverage chart: $DOMAIN_COVERAGE_OUTPUT"
echo "Saved latest question intent coverage chart: $INTENT_COVERAGE_OUTPUT"
echo "Saved latest certification coverage chart: $CERTIFICATION_COVERAGE_OUTPUT"
echo "Saved accuracy metrics chart: $ACCURACY_CHART_OUTPUT"
echo "Saved question coverage chart: $QUESTION_COVERAGE_CHART_OUTPUT"
echo "Saved latest release report $REPORT_OUTPUT"
echo "Saved latest curated rubric review $RUBRIC_REVIEW_OUTPUT"

if [ "$TEST_STATUS" -ne 0 ]; then
  echo "Release metrics were generated, but one or more pre-release test suites failed." >&2
  exit "$TEST_STATUS"
fi
