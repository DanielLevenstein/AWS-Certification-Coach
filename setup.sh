#!/bin/bash
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
# Ensure the directory exists
mkdir -p data/curated
cp -f config/curated_training_data.json data/curated/curated_training_data.json
pip3 install -e .
bash generate_data.sh