# Release v1.2 task list
- Move all md docs except for the base level README into a docs' folder.
- Identify if the rating functions for accuracy and mse need to remain separate or if they can be combined.
- Copy curated_training_data.json to data/curated dir creating a new version of the file if any changes are found.
- verify that data in user_feedback.v1.json is handled as part of the unit test suite.
- Update the model to store separate model weights for the three parts of the evaluation process based on info in ARCHITECTURE.md
- Separate model evaluation from a unit test based on info in DESIGN.md
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 

Update this file with a timestamp and agent changes.