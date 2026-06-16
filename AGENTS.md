# Project Setup
- Do not autorun streamlit app on opening codespace.
- Run all python code in a virtual environment.
- run setup.sh if a script is available, and if it's not, locate a data generation script instead.

## Documentation Files.
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
