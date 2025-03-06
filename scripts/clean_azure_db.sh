#!/bin/bash

# Exit on error
set -ex

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Load Azure configuration
source scripts/azure_config.sh

# Verify the connection string (will be hidden in logs)
echo "Testing database connection..."

export FLASK_APP="wsgi.py"
export FLASK_ENV="production"

# Use the same DATABASE_URL for both psql and Flask
export DATABASE_URL="postgresql://maisondbadmin:Uwas-30236224%7B%7D@maison-db.postgres.database.azure.com/property_db?sslmode=require"
export SQLALCHEMY_DATABASE_URI="$DATABASE_URL"

# Drop and recreate the schema
echo "Dropping and recreating schema..."
psql "$DATABASE_URL" -c "DROP SCHEMA public CASCADE;"
psql "$DATABASE_URL" -c "CREATE SCHEMA public;"

# Run the Python reset script that creates empty tables
python scripts/clean_azure_db.py

# Check the exit status
if [ $? -ne 0 ]; then
    echo "Error: Database reset failed"
    exit 1
fi

echo "Database has been reset successfully with empty tables!" 