#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" -m pytest
"$PYTHON_BIN" scripts/release_metrics.py

echo "After script is run update RELEASE_NOTES and push image to docker with the following commands"
echo "docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:latest . --push"
echo "Docker image URL: https://docker.io/daniellevenstein/aws-certification-coach:latest"
