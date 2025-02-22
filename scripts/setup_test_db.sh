#!/bin/bash

# Exit on error and print commands
set -ex

echo "Setting up test database..."

# Check if PostgreSQL is running
if ! pg_isready; then
    echo "Error: PostgreSQL is not running"
    exit 1
fi

echo "Current Python path: $PYTHONPATH"
echo "Current directory: $(pwd)"

echo "Dropping existing test database..."
dropdb test_db --if-exists

echo "Creating fresh test database..."
createdb test_db

echo "Setting environment variables..."
# Set environment variables for testing
export FLASK_APP=wsgi.py
export FLASK_ENV=testing
export TEST_DATABASE_URL="postgresql://roblovegrove@localhost:5432/test_db"
export PYTHONPATH="$(pwd):${PYTHONPATH:-}"  # Add current directory to Python path

echo "Checking Flask app..."
flask --version

echo "Checking database URL..."
python3 -c "
from app import create_app
app = create_app('testing')
with app.app_context():
    print(f'Database URL: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')
"

echo "Creating database tables..."
python3 -c "
from app import create_app, db
from sqlalchemy import inspect
app = create_app('testing')
with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    print('Tables created:', inspector.get_table_names())
"

echo "Verifying database tables..."
psql -h localhost -U roblovegrove -d test_db -c "\dt"

echo "Cleaning up existing tables..."
psql -h localhost -U roblovegrove -d test_db -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO roblovegrove;
GRANT ALL ON SCHEMA public TO public;
"

echo "Creating fresh tables..."
python3 -c "
from app import create_app, db
app = create_app('testing')
with app.app_context():
    db.create_all()
"

echo "Running tests..."
pytest -v --tb=short

# Clean up only if tests passed
if [ $? -eq 0 ]; then
    echo "Tests passed! Cleaning up..."
    dropdb test_db
else
    echo "Tests failed! Keeping database for inspection."
    exit 1
fi

echo "Test setup and execution complete!" 