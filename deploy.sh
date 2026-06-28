#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $0 [--pre_release] <tag_id>" >&2
  echo "Example: $0 v1.5.4" >&2
  echo "Example: $0 --pre_release v1.5.4" >&2
}

PRE_RELEASE=0
TAG_ID=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --pre_release|--pre-release)
      PRE_RELEASE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      usage
      echo "Unknown option: $1" >&2
      exit 2
      ;;
    *)
      if [ -n "$TAG_ID" ]; then
        usage
        echo "Unexpected extra argument: $1" >&2
        exit 2
      fi
      TAG_ID="$1"
      shift
      ;;
  esac
done

if [ -z "$TAG_ID" ]; then
  usage
  exit 2
fi

IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-daniellevenstein/aws-certification-coach}"
TAG_IMAGE="${IMAGE_REPOSITORY}:${TAG_ID}"
LATEST_IMAGE="${IMAGE_REPOSITORY}:latest"
PRE_RELEASE_IMAGE="${IMAGE_REPOSITORY}:pre_release"
DATABASE_IMAGE="${DATABASE_IMAGE:-mongo:7}"
DATABASE_IMAGE_REPOSITORY="${DATABASE_IMAGE_REPOSITORY:-daniellevenstein/aws-certification-coach-mongodb}"
DATABASE_TAG_IMAGE="${DATABASE_IMAGE_REPOSITORY}:${TAG_ID}"
DATABASE_LATEST_IMAGE="${DATABASE_IMAGE_REPOSITORY}:latest"
DATABASE_PRE_RELEASE_IMAGE="${DATABASE_IMAGE_REPOSITORY}:pre_release"
COMPOSE_APP_IMAGE="${COMPOSE_APP_IMAGE:-aws-certification-coach:compose}"
RELEASE_NOTES="RELEASE_NOTES.md"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-aws-certification-coach-pre-release}"
COMPOSE_CLEANUP=0

compose_pre_release_cleanup() {
  status=$?
  if [ "$COMPOSE_CLEANUP" -eq 1 ]; then
    if [ "$status" -ne 0 ]; then
      mkdir -p metrics/deployment
      compose_pre_release logs --no-color > metrics/deployment/compose-pre-release.log 2>&1 || true
      echo "Compose pre-release logs written to metrics/deployment/compose-pre-release.log" >&2
    fi
    compose_pre_release down --remove-orphans >/dev/null 2>&1 || true
  fi
}

compose_pre_release() {
  docker compose -f compose.yaml -f compose.pre-release.yaml "$@"
}

run_compose_pre_release() {
  export COMPOSE_APP_IMAGE
  export COMPOSE_PROJECT_NAME

  echo "Running Docker Compose pre-release check with project: $COMPOSE_PROJECT_NAME"
  compose_pre_release --profile tools config >/dev/null
  COMPOSE_CLEANUP=1
  trap compose_pre_release_cleanup EXIT INT TERM
  compose_pre_release down --remove-orphans >/dev/null 2>&1 || true
  compose_pre_release build app
  compose_pre_release up -d mongodb
  compose_pre_release up -d app
  app_container="$(compose_pre_release ps -q app)"
  if [ -z "$app_container" ]; then
    echo "Compose pre-release failed: app container was not created." >&2
    exit 1
  fi
  i=0
  while [ "$i" -lt 60 ]; do
    health_status="$(docker inspect --format '{{.State.Health.Status}}' "$app_container" 2>/dev/null || true)"
    if [ "$health_status" = "healthy" ]; then
      break
    fi
    if [ "$health_status" = "unhealthy" ]; then
      echo "Compose pre-release failed: app container became unhealthy." >&2
      exit 1
    fi
    i=$((i + 1))
    sleep 1
  done
  if [ "$health_status" != "healthy" ]; then
    echo "Compose pre-release failed: app container did not become healthy." >&2
    exit 1
  fi
  compose_pre_release exec -T app python -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=10).read().strip() == b'ok'"
  compose_pre_release exec -T app python -c "import urllib.request; body = urllib.request.urlopen('http://127.0.0.1:8501/', timeout=10).read(); assert b'streamlit' in body.lower() or b'AWS Certification Coach' in body"
  docker tag "$COMPOSE_APP_IMAGE" "$PRE_RELEASE_IMAGE"
  echo "Compose pre-release image tagged: $PRE_RELEASE_IMAGE"
  compose_pre_release_cleanup
  trap - EXIT INT TERM
  COMPOSE_CLEANUP=0
}

push_pre_release_images() {
  docker buildx imagetools inspect "$DATABASE_IMAGE" >/dev/null
  echo "Database image available: $DATABASE_IMAGE"
  docker buildx imagetools create -t "$DATABASE_PRE_RELEASE_IMAGE" "$DATABASE_IMAGE"
  echo "Database pre-release image pushed: $DATABASE_PRE_RELEASE_IMAGE"

  docker buildx build --platform linux/amd64 -t "$PRE_RELEASE_IMAGE" . --push
  echo "App pre-release image pushed: $PRE_RELEASE_IMAGE"
}

if [ -n "$(git status --porcelain)" ]; then
  if [ "$PRE_RELEASE" -eq 0 ]; then
    echo "Deploy aborted: commit or stash local changes before deploying." >&2
    git status --short >&2
    exit 1
  fi
  echo "Deploy pre_release: local changes will only be used for the Compose pre-release check." >&2
  git status --short >&2
fi

if [ "$PRE_RELEASE" -eq 0 ] && ! grep -Fq "$TAG_ID" "$RELEASE_NOTES"; then
  echo "Deploy aborted: release tag '$TAG_ID' was not found in $RELEASE_NOTES." >&2
  echo "Update RELEASE_NOTES.md with this release before deploying." >&2
  exit 1
fi

if [ "$PRE_RELEASE" -eq 0 ] && [ -z "${MONGODB_URI:-}" ]; then
  echo "Deploy aborted: MONGODB_URI must be set for the target database service." >&2
  echo "Example: MONGODB_URI='mongodb+srv://user:pass@example.mongodb.net/aws_certification_coach' $0 $TAG_ID" >&2
  exit 1
fi

if [ "$PRE_RELEASE" -eq 0 ] && [ -z "${AWS_COACH_MONGODB_DATABASE:-}" ]; then
  echo "Deploy aborted: AWS_COACH_MONGODB_DATABASE must be set." >&2
  echo "Example: AWS_COACH_MONGODB_DATABASE='aws_certification_coach' $0 $TAG_ID" >&2
  exit 1
fi

run_compose_pre_release

if [ "$PRE_RELEASE" -eq 1 ]; then
  push_pre_release_images
  echo "Pre-release check complete. Docker pre-release images were pushed."
  exit 0
fi

docker buildx imagetools inspect "$DATABASE_IMAGE" >/dev/null
echo "Database image available: $DATABASE_IMAGE"
docker buildx imagetools create -t "$DATABASE_TAG_IMAGE" -t "$DATABASE_LATEST_IMAGE" "$DATABASE_IMAGE"
echo "Database image pushed: $DATABASE_TAG_IMAGE"
echo "Database image pushed: $DATABASE_LATEST_IMAGE"

docker buildx build --platform linux/amd64 -t "$TAG_IMAGE" -t "$LATEST_IMAGE" . --push

echo "Deploy image pushed: $TAG_IMAGE"
echo "Deploy image pushed: $LATEST_IMAGE"
echo "Database image required by deployment: $DATABASE_TAG_IMAGE"
echo "Reminder: merge this branch into main in GitHub, create the GitHub tag, and redeploy the Streamlit app."
