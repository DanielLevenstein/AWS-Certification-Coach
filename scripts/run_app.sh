#!/usr/bin/env sh
set -e

# This script is intentionally safe and will not autorun on Codespace open.
# It provides a convenient entrypoint to start the app when you explicitly run it.

if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
elif [ -f venv/bin/activate ]; then
  . venv/bin/activate
fi

echo "To run the app, uncomment the desired command below and re-run this script."
# Example commands (uncomment one to use):
# python app.py
# python -m streamlit run app.py

exit 0
