# Release Workflow

## Required Checks

Run commands through the project virtual environment or existing shell wrappers:

```bash
./clean.sh
./setup.sh
./run_unit_tests.sh
./run_model_smoke_tests.sh
./run_model_training_tests.sh
./release_notes.sh --full <release-tag>
```

Use `./release_notes_full.sh` before any code commit. It writes metrics under ignored directories and updates release artifacts.

## Release Notes

Update `docs/RELEASE_NOTES.md` with:

- A one-line description of the change.
- The latest release metrics table.
- A comment below the table when model performance is below the quality standard.

For question expansion, add a `question fidelity` metric displayed as a percentage in release notes. Keep it separate from answer semantic accuracy, precision, and recall.

## Guardrails

- Do not push Docker images or create GitHub tags before human review.
- Confirm generated data and metrics are not staged.
- Keep `todo.md` changes out of refactoring work unless explicitly requested.
- Do not merge question-fidelity thresholds with answer-scoring thresholds.
