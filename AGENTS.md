# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run setup.sh if a script is available, and if it's not, locate a data generation script instead.
- Copy config/curated_training_data.json to data/curated folder.

# Helper scripts

Ensure the following scripts exist in the root directory of the current branch.

- clean.sh - Deletes all data in data directory
- setup.sh - Generate training
- generate_metrics.sh - Generates metrics for release
- run_tests.sh - Runs pytest
- run_app.sh - Run streamlit app in venv

Move all script files except those into the script dir


# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control.
- Ensure no files in data directory are committed
- validate that all sh scripts create a virtual environment.
- run a clean script which deletes all files in the data directory.

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit.
Remove completed items from todo.md as a separate commit
