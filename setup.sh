#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PYTHON_BIN=".venv/bin/python"
"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" scripts/download_developer_original_questions.py
"$PYTHON_BIN" scripts/generate_sample_training_artifacts.py
"$PYTHON_BIN" scripts/generate_app_question_artifacts.py --count 80
"$PYTHON_BIN" scripts/generate_developer_question_artifacts.py --app-output data/questions/sample_questions.json
mkdir -p data/generated data/curated
cp -p config/user_feedback.v1.json data/generated/user_feedback.v1.json
cp -p config/generated_feedback.vs.json data/generated/generated_feedback.vs.json
cp -p config/curated_training_data.json data/curated/curated_training_data.json
"$PYTHON_BIN" scripts/combine_curated_training_data.py
