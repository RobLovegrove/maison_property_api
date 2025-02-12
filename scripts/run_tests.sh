#!/bin/bash

# Create test database if it doesn't exist
createdb property_db_test 2>/dev/null || true

# Run pytest with verbose output
PYTHONPATH=. pytest -v tests/ 