#!/usr/bin/env bash
set -euo pipefail

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

"$PYTHON_BIN" -m pytest
"$PYTHON_BIN" scripts/release_metrics.py

echo "After script is run update RELEASE_NOTES and push image to docker with the following commands"
echo "docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:tag . --push"
echo "Test tagged build before pushing to latest:"
echo "docker run -p 8501:8501 daniellevenstein/aws-certification-coach:tag"
echo "Then build and push latest image."
echo "docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:latest . --push"
echo "Docker image URL: https://docker.io/daniellevenstein/aws-certification-coach:latest"
