# Check and restore required scripts if missing
for file in setup.sh generate_data.sh run_tests.sh generate_metrics.sh run_app.sh; do
    if [ ! -f "$file" ]; then
        cp "${file}_COPY.*" "$file"
    fi
done

# Backup the specified required files
for file in setup.sh generate_data.sh run_tests.sh generate_metrics.sh run_app.sh docs_clean.sh; do
    cp "$file" "${file}_COPY.*.sh"
done

# Move all other .sh files (except specified ones) into the 'scripts' directory
find . -maxdepth 1 -type f -name '*.sh' ! -name 'setup.sh' ! -name 'generate_data.sh' ! -name 'run_tests.sh' ! -name 'generate_metrics.sh' ! -name 'run_app.sh' ! -name 'docs_clean.sh' -exec mv {} scripts/ \;

# Move all .md files from the root directory (except specific ones) into the 'docs' directory
find . -maxdepth 1 -type f -name '*.md' ! -name 'README.md' ! -name 'todo.md' ! -name 'CHECKLIST.md' -exec cp {} "{}_COPY.*" \; -exec mv {} docs/ \;
