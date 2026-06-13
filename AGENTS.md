# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run setup.sh if a script is available, and if it's not, locate a data generation script instead.

# Helper scripts

- clean.sh
- setup.sh
- generate_data.sh
- run_tests.sh
- generate_metrics.sh
- run_app.sh

Move all script files except those into the script dir 

## Documentation Files.
- Move all documentation files except README.md, todo.md and AGENTS.md, and live in the docs directory.
- Create a backup TODO file called TODO_COPY.md 
- Create a backup copy of AGENTS.md called AGENTS_COPY.md
- Ensure no copy files are committed to source control 

# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control. 
- Ensure no files in data directory are committed
- validate that all sh scripts create a virtual environment.
- run a clean script which deletes all files in the data directory.
- run setup script
- Ensure test cases are using verification data, not training data.
- Get all unit tests passing, adding comments for updated tests. 
- delete data directory 
- Ensure all code is committed 

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit. 
Remove completed items from todo.md as a separate commit
