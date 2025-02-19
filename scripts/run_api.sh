#!/bin/bash

# Set environment variables
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL="postgresql://maisondbadmin:Uwas-30236224%7B%7D@maison-db.postgres.database.azure.com/property_db?sslmode=require"
export PYTHONPATH=.

echo "Starting MaiSON Property API..."
echo "Database: Azure PostgreSQL"
echo "Environment: Development"
echo "Debug Mode: Enabled"
echo "URL: http://localhost:8080"
echo "-----------------------------------"

# Run the Flask application
flask run -h localhost -p 8080 