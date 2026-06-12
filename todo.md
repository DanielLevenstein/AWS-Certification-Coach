- Create a changes.log file with timestamps and a one-line summary of changes. Update the file at the end of each section break. 
- Create an agents.md file with previous human feedback which is not dependent on specific features being implemented.
- Create a script which moves all root level md files into the docs folder.
- $version value in feature branches should match the version of the release branch it was branches off of ex: v1.1.2
- Commit changes at the end of each section after verifying that unit tests pass. If unit tests do not pass, add comments to the test and wait for human feedback. 

# Test Framework Redesign
- Create a branch for features/test_redesign_$version  
- Separate model evaluation from a unit test based on info in DESIGN.md
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 
- Create a patch file for changes so they can be applied on different branches but don't commit a patch file
- Commit changes at the end of each section after verifying that unit tests pass. If unit tests do not pass, add comments to the test and wait for human feedback. 

# Model Combinations
- Create a branch feature/model_combination_$version  
- Create a design document for merging partial answer classifier and full answer classifier into a single model.
- Include data in docs/images as unlabeled test data for the classification algorithm.
- Commit changes at the end of each section after verifying that unit tests pass. If unit tests do not pass, add comments to the test and wait for human feedback. 
