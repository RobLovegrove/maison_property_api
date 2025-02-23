#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set Flask-specific environment variables
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export PYTHONPATH=.

echo "Starting MaiSON Property API..."
echo "PYTHONPATH: $PYTHONPATH"
echo "FLASK_APP: $FLASK_APP"
echo "FLASK_ENV: $FLASK_ENV"
echo "Database: Azure PostgreSQL"
echo "Environment: Development"
echo "Debug Mode: Enabled"
echo "URL: http://localhost:8000"
echo "-----------------------------------"

# Run the Flask application
flask run -h localhost -p 8000 