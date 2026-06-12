# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run setup.sh if a script is available, and if it's not, locate a data generation script instead.

# Helper scripts

ensure the following scripts exist in the current branch, and if they don't, copy them from $FILE$_COPY.*
- setup.sh
- generate_data.sh
- run_tests.sh
- generate_metrics.sh
- run_app.sh

Move all script files except those into the script dir

## Documentation Move.
- Move all documentation files except README.md, todo.md  CHECKLIST.md, and AGENTS.md
- Make backup copies of all files mentioned above with format $FILE$_COPY.* 
- Ensure that COPY files are not added to source control.

# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control. 
- Ensure no files in data directory are committed
- run a clean script which deletes all files in the data directory.
- Regenerate training data.
- Ensure test cases are using verification data, not training data.
- Copy config/curated_training_data.json to data/curated folder. 
- Get all unit tests passing, adding comments for updated tests. 
- Ensure all code is committed 

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit. 
Remove completed items from todo.md as a separate commit
