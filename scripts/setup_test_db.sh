#!/bin/bash

# Drop test database if it exists
dropdb maison_test --if-exists

# Create test database
createdb maison_test

# Set up test environment
export FLASK_APP=app.main:app
export FLASK_ENV=testing
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/maison_test"
export PYTHONPATH=.

# Run tests
pytest tests/ -v 