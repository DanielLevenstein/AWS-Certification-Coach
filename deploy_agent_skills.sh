#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

SOURCE_DIR="skills"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
DRY_RUN=0

usage() {
  cat <<USAGE
Usage: scripts/deploy_agent_skills.sh [--dry-run] [--source <dir>] [--target <dir>]

Deploy repo-local agent skills for future Codex agents.

Options:
  --dry-run       Print planned deployments without copying files.
  --source <dir> Source skill directory. Defaults to skills.
  --target <dir> Destination skill directory. Defaults to $TARGET_DIR.
  -h, --help      Show this help.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --source)
      if [ "$#" -lt 2 ]; then
        echo "Missing value for --source" >&2
        exit 2
      fi
      SOURCE_DIR="$2"
      shift 2
      ;;
    --target)
      if [ "$#" -lt 2 ]; then
        echo "Missing value for --target" >&2
        exit 2
      fi
      TARGET_DIR="$2"
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Skill source directory does not exist: $SOURCE_DIR" >&2
  exit 1
fi

DEPLOYED=0
for SKILL_PATH in "$SOURCE_DIR"/*; do
  if [ ! -d "$SKILL_PATH" ]; then
    continue
  fi

  SKILL_NAME="$(basename "$SKILL_PATH")"
  if [ ! -f "$SKILL_PATH/SKILL.md" ]; then
    echo "Skipping $SKILL_NAME: missing SKILL.md" >&2
    continue
  fi

  DESTINATION="$TARGET_DIR/$SKILL_NAME"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would deploy $SKILL_PATH -> $DESTINATION"
    DEPLOYED=$((DEPLOYED + 1))
    continue
  fi

  mkdir -p "$TARGET_DIR"
  STAGING_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agent-skill-deploy.XXXXXX")"
  trap 'rm -rf "$STAGING_DIR"' EXIT HUP INT TERM
  cp -R "$SKILL_PATH" "$STAGING_DIR/$SKILL_NAME"
  rm -rf "$DESTINATION"
  mv "$STAGING_DIR/$SKILL_NAME" "$DESTINATION"
  rm -rf "$STAGING_DIR"
  trap - EXIT HUP INT TERM

  echo "Deployed $SKILL_NAME -> $DESTINATION"
  DEPLOYED=$((DEPLOYED + 1))
done

if [ "$DEPLOYED" -eq 0 ]; then
  echo "No deployable skills found in $SOURCE_DIR" >&2
  exit 1
fi

echo "Agent skill deployment complete. Skills deployed: $DEPLOYED"
