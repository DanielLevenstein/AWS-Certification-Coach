#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <release-tag>" >&2
  echo "Example: $0 v1.3.2" >&2
  exit 2
fi

RELEASE_TAG="$1"
case "$RELEASE_TAG" in
  v[0-9]*.[0-9]*.[0-9]* | v[0-9]*.[0-9]*.[0-9]*.[0-9]*) ;;
  *)
    echo "Release tag must look like v1.3.2; received: $RELEASE_TAG" >&2
    exit 2
    ;;
esac

METRICS_DIR="metrics/$(date '+%Y%m%d_%H%M%S')"
.venv/bin/python test_suites.py release --release-label "$RELEASE_TAG" --release-notes docs/RELEASE_NOTES.md --metrics-dir "$METRICS_DIR"

ACCURACY_SOURCE="$METRICS_DIR/semantic_accuracy.png"
ACCURACY_OUTPUT="release/${RELEASE_TAG}_semantic_accuracy.png"
mkdir -p release
cp -p "$ACCURACY_SOURCE" "$ACCURACY_OUTPUT"
echo "Saved tagged accuracy chart: $ACCURACY_OUTPUT"
