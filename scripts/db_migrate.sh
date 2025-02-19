#!/bin/bash

# Set up production environment
export FLASK_APP=app.main:app
export FLASK_ENV=production
export DATABASE_URL="postgresql://maisondbadmin:Uwas-30236224%7B%7D@maison-db.postgres.database.azure.com/property_db?sslmode=require"
export PYTHONPATH=.

# Initialize migrations if they don't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations..."
    flask db init
fi

# Create new migration
echo "Creating new migration..."
flask db migrate -m "Database migration $(date +%Y%m%d_%H%M%S)"

# Apply migration
echo "Applying migration..."
flask db upgrade

echo "Migration complete!" 