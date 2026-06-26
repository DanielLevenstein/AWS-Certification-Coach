#!/usr/bin/env sh
set -eu

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PYTHON_BIN=".venv/bin/python"
"$PYTHON_BIN" -m pip install -r requirements.txt
"$PYTHON_BIN" scripts/download_developer_original_questions.py
"$PYTHON_BIN" scripts/generate_app_question_artifacts.py
"$PYTHON_BIN" scripts/generate_developer_question_artifacts.py --app-output data/questions/sample_questions.json
"$PYTHON_BIN" scripts/generate_question_rewording_training_data.py
mkdir -p data/generated data/curated
cp -p config/data/structured_answer_training_data.json data/curated/structured_answer_training_data.json
if [ ! -f data/generated/user_feedback.v2.json ]; then
  printf '[]\n' > data/generated/user_feedback.v2.json
fi

"$PYTHON_BIN" scripts/combine_curated_training_data.py
