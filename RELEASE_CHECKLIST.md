# Refactoring checklist

For each merge ensure the following.

- Keep roadmap changes separate from unrelated refactoring commits.
- Ensure generated `data/`, `scripts/data/`, and `metrics/` files are not committed.
- Run `./clean.sh` before regeneration when schemas or generated behavior change.
- Regenerate training data.
- Ensure test cases are using verification data, not training data.
- Keep versioned structured training sources separate from generated runtime copies.
- Get all unit tests passing, adding comments for updated tests.
- Files ending in _COPY which do not have local copies should be used as templates to create missing files
- Files ending in COPY should not be committed to source control.
- For agent skill changes, follow `docs/AGENT_SKILL_RELEASE_INSTRUCTIONS.md`.
- For v3 model changes, follow the design, architecture, and metrics contracts under `docs/V3_LOCAL_SEMANTIC_ANSWER_GRADING_*.md`.

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit.
Remove completed items from todo.md as a separate commit
