
# Documentation Cleanup
- Move all md docs except for the base level README into a docs' folder.

# Test Framework Redesign
- Create a branch for features/test_redesign_$version  
- Separate model evaluation from a unit test based on info in DESIGN.md
- Delete test cases which are no longer relevant.
- Update training code so it evaluates answers against training data multiple times and generates a graph showing how model performance improved over time. 
- Write root-level helper functions for each of the three test suites in the new test framework.
- Create scripts to measure cyclomatic complexity and code coverage, call these from the release_metrics.sh script. 

## Model performance Optimization

Recommended Remediation Order
- Reconcile conflicting curated labels before changing model code.
- Add normalized AWS service aliases and semantic service-match features.
- Add concept-coverage features that are independent of full reference-answer overlap.
- Calibrate grade boundaries against curated examples rather than relying only on regression MSE.
- Revisit runtime exact-option and wrong-service guards so partial-credit expectations are represented consistently.