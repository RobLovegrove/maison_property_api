#!/bin/bash
# Ensure virtual environment is activated
source .venv/bin/activate
export FLASK_APP=app/main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8080 