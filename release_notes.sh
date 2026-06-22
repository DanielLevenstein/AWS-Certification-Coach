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

if [ "$MODE" = "full" ]; then
  .venv/bin/python test_suites.py model
fi

METRICS_DIR="metrics/$(date '+%Y%m%d_%H%M%S')"
if [ "$STRICT_GRADING" = "1" ]; then
  .venv/bin/python test_suites.py release \
    --release-label "$RELEASE_TAG" \
    --release-notes RELEASE_NOTES.md \
    --metrics-dir "$METRICS_DIR" \
    --strict-grading
else
  .venv/bin/python test_suites.py release \
    --release-label "$RELEASE_TAG" \
    --release-notes RELEASE_NOTES.md \
    --metrics-dir "$METRICS_DIR"
fi

ACCURACY_SOURCE="$METRICS_DIR/semantic_accuracy.png"
ACCURACY_OUTPUT="release/semantic_accuracy.png"
PER_GRADE_PRECISION_SOURCE="$METRICS_DIR/per_grade_precision.png"
PER_GRADE_PRECISION_OUTPUT="release/per_grade_precision.png"
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
cp -p "$ACCURACY_SOURCE" "$ACCURACY_OUTPUT"
cp -p "$PER_GRADE_PRECISION_SOURCE" "$PER_GRADE_PRECISION_OUTPUT"
cp -p "$DOMAIN_COVERAGE_SOURCE" "$DOMAIN_COVERAGE_OUTPUT"
cp -p "$INTENT_COVERAGE_SOURCE" "$INTENT_COVERAGE_OUTPUT"
cp -p "$CERTIFICATION_COVERAGE_SOURCE" "$CERTIFICATION_COVERAGE_OUTPUT"
cp -p "$LATEST_REPORT" "$REPORT_OUTPUT"
cp -p "$LATEST_RUBRIC_REVIEW" "$RUBRIC_REVIEW_OUTPUT"
.venv/bin/python scripts/combine_release_charts.py \
  --semantic-accuracy "$ACCURACY_OUTPUT" \
  --per-grade-precision "$PER_GRADE_PRECISION_OUTPUT" \
  --domain-coverage "$DOMAIN_COVERAGE_OUTPUT" \
  --intent-coverage "$INTENT_COVERAGE_OUTPUT" \
  --certification-coverage "$CERTIFICATION_COVERAGE_OUTPUT" \
  --accuracy-output "$ACCURACY_CHART_OUTPUT" \
  --coverage-output "$QUESTION_COVERAGE_CHART_OUTPUT"
cp -p "$ACCURACY_CHART_OUTPUT" "release/${RELEASE_TAG}"_accuracy_metrics_chart.png
cp -p "$QUESTION_COVERAGE_CHART_OUTPUT" "release/${RELEASE_TAG}"_question_coverage_chart.png

echo "Saved latest accuracy chart: $ACCURACY_OUTPUT"
echo "Saved latest per-grade precision chart: $PER_GRADE_PRECISION_OUTPUT"
echo "Saved latest domain coverage chart: $DOMAIN_COVERAGE_OUTPUT"
echo "Saved latest question intent coverage chart: $INTENT_COVERAGE_OUTPUT"
echo "Saved latest certification coverage chart: $CERTIFICATION_COVERAGE_OUTPUT"
echo "Saved accuracy metrics chart: $ACCURACY_CHART_OUTPUT"
echo "Saved question coverage chart: $QUESTION_COVERAGE_CHART_OUTPUT"
echo "Saved latest release report $REPORT_OUTPUT"
echo "Saved latest curated rubric review $RUBRIC_REVIEW_OUTPUT"
