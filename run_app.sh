#!/usr/bin/env sh
set -e

# This script is intentionally safe and will not autorun on Codespace open.
# It provides a convenient entrypoint to start the app when you explicitly run it.

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

echo "To run the app, uncomment the desired command below and re-run this script."
# Example commands (uncomment one to use):
 .venv/bin/python app.py
 .venv/bin/python -m streamlit run app.py

exit 0
