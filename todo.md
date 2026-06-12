# Migrate from v1.1.2 to v2
- Release branch v1.1.2 is going to be moved to release/v2 but we should make sure all unit tests pass and all branches are merged in before doing so. 

- Create a changes.log file with timestamps and a one-line summary of changes. Update the file at the end of each section break. 
- Create an agents.md file with previous human feedback which is not dependent on specific features being implemented.
- $version value in feature branches should match the version of the release branch it was branches off of ex: v1.1.2
- Commit changes at the end of each section after verifying that unit tests pass. If unit tests do not pass, add comments to the test and wait for human feedback. 
