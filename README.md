# Property Listings API

A Flask-based REST API for managing real estate properties.

## Setup

### Prerequisites
- Python 3.7+
- PostgreSQL 14
- libpq

### Installation

1. Clone the repository
```bash
git clone [repository-url] properties_api
cd properties_api
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r app/requirements.txt
```

4. Set up PostgreSQL (macOS)
```bash
# Install PostgreSQL
brew install postgresql@14 libpq

# Start PostgreSQL service
brew services start postgresql@14

# Create database user and database
createuser -s postgres
createdb property_db
```

### Running the Application

1. Seed the database with sample data
```bash
PYTHONPATH=. python scripts/seed_database.py
```

2. Start the development server
```bash
./scripts/run_local.sh
```

The API will be available at `http://localhost:8080`

## Database Management

### Direct Database Access
Connect to the database using psql:
```bash
psql property_db
```

Useful psql commands:
```sql
\dt                     -- List all tables
\d properties           -- Show table structure
\q                      -- Quit psql

-- Query examples
SELECT * FROM properties;
SELECT address, price FROM properties WHERE bedrooms > 2;
SELECT property_type, COUNT(*) FROM properties GROUP BY property_type;
```

## API Endpoints

### Properties
- `GET /api/properties` - List all properties
  - Query parameters:
    - `property_type`: Filter by property type
    - `min_price`: Minimum price
    - `max_price`: Maximum price
    - `min_beds`: Minimum number of bedrooms
- `GET /api/properties/<id>` - Get specific property

## Development

### Project Structure
```
/
├── app/
│   ├── main.py          # Main application file
│   ├── models.py        # Database models
│   ├── config.py        # Configuration
│   └── requirements.txt # Python dependencies
├── scripts/
│   ├── run_local.sh     # Local development server script
│   └── seed_database.py # Database seeding script
├── Dockerfile           # Container configuration
└── cloudbuild.yaml      # Google Cloud Build configuration
```

### Docker Support
Build the container:
```bash
docker build -t property-api .
```

Run the container:
```bash
docker run -p 8080:8080 property-api
```

## Contributing
[Add contribution guidelines]

## License
[Add license information]
