#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <tag_id>" >&2
  echo "Example: $0 v1.5.4" >&2
  exit 2
fi

TAG_ID="$1"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-daniellevenstein/aws-certification-coach}"
TAG_IMAGE="${IMAGE_REPOSITORY}:${TAG_ID}"
LATEST_IMAGE="${IMAGE_REPOSITORY}:latest"
RELEASE_NOTES="RELEASE_NOTES.md"

if [ -n "$(git status --porcelain)" ]; then
  echo "Deploy aborted: commit or stash local changes before deploying." >&2
  git status --short >&2
  exit 1
fi

if ! grep -Fq "$TAG_ID" "$RELEASE_NOTES"; then
  echo "Deploy aborted: release tag '$TAG_ID' was not found in $RELEASE_NOTES." >&2
  echo "Update RELEASE_NOTES.md with this release before deploying." >&2
  exit 1
fi


.venv/bin/python scripts/check_precision_guardrails.py --release-label "$TAG_ID"


.venv/bin/python -m pip install -e . --quiet
.venv/bin/python -m pip install pytest --quiet

docker buildx build --platform linux/amd64 -t "$TAG_IMAGE" --load .
DOCKER_IMAGE="$TAG_IMAGE" ./run_deployment_tests.sh

docker buildx build --platform linux/amd64 -t "$TAG_IMAGE" -t "$LATEST_IMAGE" . --push

echo "Deploy image pushed: $TAG_IMAGE"
echo "Deploy image pushed: $LATEST_IMAGE"
echo "Reminder: merge this branch into main in GitHub, create the GitHub tag, and redeploy the Streamlit app."
