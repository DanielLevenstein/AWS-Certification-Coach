#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python"
fi

"$PYTHON_BIN" -m pytest
"$PYTHON_BIN" scripts/release_metrics.py

echo "After script is run update RELEASE_NOTES and push image to docker with the following commands"
echo "docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:tag. --push"
echo "Test tagged build before pushing to latest"
echo "docker run -p 8501:8501 daniellevenstein/aws-certification-coach:tag"
echo "Docker image URL: https://docker.io/daniellevenstein/aws-certification-coach:latest"
