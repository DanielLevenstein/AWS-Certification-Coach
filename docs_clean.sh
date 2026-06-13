# Move all .md files from the root directory with names in all uppercase letters to the 'docs' directory
find . -maxdepth 1 -type f -name '[A-Z]*.md' -exec mv {} docs/ \;
