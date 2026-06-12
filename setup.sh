set -euo pipefail

PTYONPATH=src
rm -rf data

# Check if the user is already in a virtual environment
if [ -z "${VIRTUAL_ENV-}" ]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        python -m venv venv
        source venv/bin/activate
    fi
fi

python -m pip install -r requirements.txt
python scripts/generate_sample_training_artifacts.py
python scripts/generate_app_question_artifacts.py --count 80

mkdir data/curated
cp config/curated_training_data.json data/curated



