# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo.txt, which is outside source control. 
- Ensure no files in data directory are committed
- run a clean script which deletes all files in the data directory.
- Regenerate training data.
- Ensure test cases are using verification data, not training data.
- Copy config/curated_training_data.json to data/curated folder. 
- Get all unit tests passing, adding comments for updated tests. 
- Ensure all code is committed 

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit. 
Remove completed items from todo.md as a separate commit

# Release v1.2 task list
- Release v1.2 is going to be moved to v2 because of extensive heuristic changes.
- move a todo.md list to todo.txt, which is a non-committed file.
- create an agent.md file for agent instructions which aren't feature-specific.
- Merge all feature branches with release v1.2 into this branch.
- switch to release/v2 and merge all changes. Hopefully, the merge should be clean since merge conflicts were handled here. 
