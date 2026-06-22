# Refactoring checklist
For each merge ensure the following.
- Leave the todo.md file as is copy this file to todo_copy.md, which is outside source control. 
- Ensure no files in data directory are committed
- run a clean script which deletes all files in the data directory.
- Regenerate training data.
- Ensure test cases are using verification data, not training data.
- Copy config/curated_training_data.json to data/curated folder. 
- Get all unit tests passing, adding comments for updated tests. 
- Ensure all code is committed 

If directory paths change between branches commit working changes first, then do a directory path refactoring as a clean commit. 
Remove completed items from todo.md as a separate commit

# Release Checklist
RELEASE_NOTES.md should show release notes for all builds that are pushed to docker.
README.md has a shorter release notes section for only major releases.

## Major and Minor Releases
1) Run all three test scripts prior to each release
- `run_unit_tests.sh`
- `run_model_tests.sh`
- `release_notes.sh --full <release-tag>`
2) Update RELEASE_NOTES.md with a description of the release and output from `release_notes.sh`.
3) Review the v3 exact-letter, legacy-compatible, macro, per-grade, and confusion-matrix metrics. Run `release_notes.sh --quick <release-tag>` only when model artifacts and data manifests are unchanged.
4) Verify the encoder revision and checksums, classifier provenance, split-manifest hashes, and clean-clone Docker build.
5) Deploy the Docker release after all changes are committed.
`./deploy.sh <release-tag>`
6) The deploy script validates a clean working tree, builds the `linux/amd64` tag, runs the Docker container load test, and pushes both the release tag and `latest`.
7) If the automated Docker test fails, run the tagged image locally for visual review before retrying.
`docker run -p 8501:8501 daniellevenstein/aws-certification-coach:tag`

## Major Releases
For major releases also do the following.
1) Update README.md with a description of the major release
2) Merge branch into main
3) Tag the major release in GitHub with a one-line description of the release in the title.
