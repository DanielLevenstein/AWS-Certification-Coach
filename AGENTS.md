# Project Setup

- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.

## Local Changes

- Never delete local files without permission.
- If local changes cause merge conflicts, copy the old version to filename_COPY.type prior to merge. 
- do not commit changes in data or metrics directory those are auto-generated files. 

## Project Scripts
- clean.sh: Cleans out data and metrics dir
- setup.sh: Generates training data for a project
- release_notes.sh --quick tag: Generates release the report for code commit. 
- run_model_smoke_tests.sh: Runs fast read-only model and knowledge contracts without training.
- run_model_training_tests.sh: Runs the temporary held-out model-training quality gate.
- train_accuracy_model.sh: Trains a timestamped candidate model and writes its diagnostic artifacts.
- run_deployment_tests.sh: Runs deployment health checks against the image named by `DOCKER_IMAGE`.

## Documentation Files
The following project documentation files have been moved to the root directory for easy use.
- README.md
- RELEASE_CHECKLIST.md
- RELEASE_NOTES.md
- TODO.md

# Commit checklist

- run `release_notes.sh --full tag` prior to every code commit.
- Update RELEASE_NOTES.md with an online description of the change.
- Update the Release Metrics section of that same document with the results from the release_notes_short.sh script.
