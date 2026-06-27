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
DATABASE_IMAGE="${DATABASE_IMAGE:-mongo:7}"
DATABASE_IMAGE_REPOSITORY="${DATABASE_IMAGE_REPOSITORY:-${IMAGE_REPOSITORY}-mongodb}"
DATABASE_TAG_IMAGE="${DATABASE_IMAGE_REPOSITORY}:${TAG_ID}"
DATABASE_LATEST_IMAGE="${DATABASE_IMAGE_REPOSITORY}:latest"
COMPOSE_APP_IMAGE="${COMPOSE_APP_IMAGE:-aws-certification-coach:compose}"
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

if [ -z "${MONGODB_URI:-}" ]; then
  echo "Deploy aborted: MONGODB_URI must be set for the target database service." >&2
  echo "Example: MONGODB_URI='mongodb+srv://user:pass@example.mongodb.net/aws_certification_coach' $0 $TAG_ID" >&2
  exit 1
fi

if [ -z "${AWS_COACH_MONGODB_DATABASE:-}" ]; then
  echo "Deploy aborted: AWS_COACH_MONGODB_DATABASE must be set." >&2
  echo "Example: AWS_COACH_MONGODB_DATABASE='aws_certification_coach' $0 $TAG_ID" >&2
  exit 1
fi

.venv/bin/python -m pip install -e . --quiet
.venv/bin/python -m pip install pytest --quiet

docker compose --profile tools config >/dev/null

docker buildx imagetools inspect "$DATABASE_IMAGE" >/dev/null
echo "Database image available: $DATABASE_IMAGE"
docker buildx imagetools create -t "$DATABASE_TAG_IMAGE" -t "$DATABASE_LATEST_IMAGE" "$DATABASE_IMAGE"
echo "Database image pushed: $DATABASE_TAG_IMAGE"
echo "Database image pushed: $DATABASE_LATEST_IMAGE"

COMPOSE_APP_IMAGE="$COMPOSE_APP_IMAGE" docker compose build app
docker tag "$COMPOSE_APP_IMAGE" "$TAG_IMAGE"
DOCKER_IMAGE="$TAG_IMAGE" ./run_deployment_tests.sh

docker buildx build --platform linux/amd64 -t "$TAG_IMAGE" -t "$LATEST_IMAGE" . --push

echo "Deploy image pushed: $TAG_IMAGE"
echo "Deploy image pushed: $LATEST_IMAGE"
echo "Database image required by deployment: $DATABASE_TAG_IMAGE"
echo "Reminder: merge this branch into main in GitHub, create the GitHub tag, and redeploy the Streamlit app."
