# Agent Skill Release Instructions

Use these steps whenever an agent skill is created, updated, or removed after a feature change.

## Scope

These instructions apply to repo-local skills under `skills/` and any future project skill directories. They do not replace the project release checklist; run them in addition to the normal release and commit checks.

## Before Updating a Skill

1. Read the changed feature design, implementation notes, or release issue that caused the skill change.
2. Confirm the skill is still needed and that its trigger description matches the new workflow.
3. Keep new documentation under `docs/`, except `AGENTS.md` and `SKILL.md` files.
4. Avoid adding generated data, metrics, model checkpoints, or copied source examples to the skill.

## Skill Update Checklist

1. Update `SKILL.md` frontmatter:
   - Keep `name` lowercase with hyphens.
   - Make `description` specific enough to trigger the skill only for relevant work.
   - Do not add extra frontmatter fields.
2. Update the skill body:
   - Keep the primary workflow concise.
   - Move detailed procedures into `references/` when they are not always needed.
   - Remove template placeholders and stale instructions.
3. Update `agents/openai.yaml` when the skill name, purpose, or default prompt changes.
4. Update or add reference files only when they directly support the skill workflow.
5. Delete placeholder resource files or directories that are no longer needed.

## Validation

Run the skill validator after the update:

```bash
.venv/bin/python /Users/daniel/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

If validation fails because `PyYAML` is missing, install dependencies through the normal project virtual environment process or record the blocker in the release notes. At minimum, verify that:

- `SKILL.md` has valid YAML frontmatter.
- `name` and `description` are present.
- `agents/openai.yaml` is valid YAML when present.
- No `[TODO]` placeholders remain.

For substantial skill changes, forward-test the skill with a realistic request before release.

## Deployment

Deploy repo-local skills for future agents after validation:

```bash
scripts/deploy_agent_skills.sh
```

Preview the deployment first when changing multiple skills:

```bash
scripts/deploy_agent_skills.sh --dry-run
```

The script copies each deployable directory from `skills/` into `${CODEX_HOME:-$HOME/.codex}/skills`.

## Release Notes

When a skill change affects how agents perform project work, add a one-line entry to `docs/RELEASE_NOTES.md` describing the agent workflow change.

Examples:

- `v2.1.x | Added local semantic-model training skill for question fidelity work.`
- `v2.1.x | Updated agent skill release instructions and validation steps.`

If the skill change is tied to model training or release metrics, include the latest metrics from the release script and note any quality gate that is not met.

## Final Pre-Commit Checks

1. Run the normal release script before commit:

```bash
./release_notes.sh --full <release-tag>
```

2. Confirm generated artifacts are not staged:

```bash
git status --short data scripts/data metrics release/metrics
```

3. Confirm skill files are intentional:

```bash
git status --short skills docs
```

4. Do not push Docker images or create GitHub tags until a human reviews the release.
