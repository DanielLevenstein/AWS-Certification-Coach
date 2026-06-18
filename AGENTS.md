# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run clean.sh to clean out the data directory for any changes that brake the existing schema
- run setup.sh to regenerate test data.
- ensure that scripts/data and metrics directory aren't committed to source control

# Commit checklist
- run release_notes_full.sh prior to every code commit.
- Update RELEASE_NOTES.md with an online description of the change.
- Update the Release Metrics section of that same document with the results from the release_notes_short.sh script.
- Prior to commit, run release_notes_full.sh, and if model performance doesn't meet a code quality standard add a comment to release notes below the Release Metrics table. 

# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control. 
- Ensure no files in data directory are committed
- validate that all sh scripts create a virtual environment.
- run a clean script which deletes all files in the data directory.
- run setup script
- Ensure test cases are using verification data, not training data.
- Get all unit tests passing, adding comments for updated tests. 
