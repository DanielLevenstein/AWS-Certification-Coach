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
- `run_release_tests.sh v1.3.x`
2) Update RELEASE_NOTES.md with a description of the release and output from `run_release_tests.sh`.
3) Review `release/metrics/training_performance.png` and `release/metrics/curated_grade_accuracy.png`. Run `run_training_graph.sh` directly when only the training graphs need to be refreshed; it also preserves each run under `data/charts/`.
4) Review `release/metrics/curated_failure_report.md` and reconcile contradictory labels before tuning the model.
5) Create a docker tag for release using the following command.
`docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:tag . --push`
6) Test docker image visually before updating the latest image.
`docker run -p 8501:8501 daniellevenstein/aws-certification-coach:tag`
7) Rerun docker build with tag=latest
`docker buildx build --platform linux/amd64 -t daniellevenstein/aws-certification-coach:latest . --push`

## Major Releases
For major releases also do the following.
1) Update README.md with a description of the major release
2) Merge branch into main
3) Tag the major release in GitHub with a one-line description of the release in the title.
