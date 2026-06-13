#!/bin/bash

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip3 install -e .
pip3 install requirments.txt
streamlit run app.py
