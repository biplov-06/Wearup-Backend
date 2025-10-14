#!/bin/bash
# Bash script to create a virtualenv and install requirements on PythonAnywhere or local bash
# Run from the Backend folder

VENV_PATH="$HOME/.virtualenvs/wearup-backend"
if [ ! -d "$VENV_PATH" ]; then
  python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip
pip install -r "$(pwd)/requirements.txt"

echo "Virtualenv created/activated at $VENV_PATH"
