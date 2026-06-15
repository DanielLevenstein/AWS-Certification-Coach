
# Documentation Cleanup
- Move all md docs except for the base level README into a docs' folder.

# Test Framework Redesign
- Create a branch for features/test_redesign_$version  
- Separate model evaluation from a unit test based on info in DESIGN.md
- Delete test cases which are no longer relevant.
- Update training code so it evaluates answers against training data multiple times and generates a graph showing how model performance improved over time. 
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 
