# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run clean.sh to clean out the data directory for any changes that brake the existing schema
- run setup.sh to regenerate test data.
- ensure that scripts/data and metrics directory aren't committed to source control

# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control. 
- Ensure no files in data directory are committed
- validate that all sh scripts create a virtual environment.
- run a clean script which deletes all files in the data directory.
- run setup script
- Ensure test cases are using verification data, not training data.
- Get all unit tests passing, adding comments for updated tests. 
