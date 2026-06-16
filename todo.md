# Pre-release refactoring

- Update model release tests to use semantic precision as the release guardrail and set the threshold to 80%
- Rename current model to Semantic similarity model and update documentation appropriately. 
- Update release_notes_full.sh and release_notes_quick.sh so that they will accept tags that aren't in the correct form so that test builds are easier. 
- Run release_notes_full.sh with the tag v1.5.4 and commit changes with a one-line release summary.