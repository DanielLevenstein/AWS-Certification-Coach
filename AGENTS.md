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
- train_accuracy_model.sh: Train model based on existing training data.

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
