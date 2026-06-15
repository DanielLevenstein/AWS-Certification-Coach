
We need to clean up the test framework for our code. The existing unit tests have test fixtures hard coded into the test and are mixing multiple types of testing into a single test suite.

Also, the new rubric is grading answers too strictly, which is preventing me from releasing this version of the app. 

# Test Framework Redesign
- Create a branch for features/test_redesign_$version  
- Separate model evaluation from a unit test based on info in DESIGN.md
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 
- Create a patch file for changes so they can be applied on different branches but don't commit a patch file
- Commit changes at the end of each section after verifying that unit tests pass. If unit tests do not pass, add comments to the test and wait for human feedback. 


# Model Splitting Feature
- Create a branch for features/model_split_$version  
- Identify if the rating functions for accuracy and mse need to remain separate or if they can be combined.
- Copy curated_training_data.json to the data/curated dir, creating a new version of the file if any changes are found.
- verify that data in user_feedback.v1.json is handled as part of the unit test suite.
- Update the model to store separate model weights for the three parts of the evaluation process based on info in ARCHITECTURE.md
- Separate model evaluation from a unit test based on info in DESIGN.md
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 

Update this file with a timestamp and agent changes.