# MaiSON Property API

A Flask-based REST API powering the MaiSON real estate platform.

## Setup

### Prerequisites
- Python 3.7+
- PostgreSQL 14
- libpq

### Installation

1. Clone the repository
```bash
git clone git@github.com:RobLovegrove/maison_property_api.git properties_api
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

### Database Migrations
To manage database schema changes:

1. Initialize migrations (first time only):
```bash
export FLASK_APP=app/manage.py
flask db init
```

2. Create a new migration when models change:
```bash
flask db migrate -m "Description of changes"
```

3. Apply pending migrations:
```bash
flask db upgrade
```

4. Rollback migrations if needed:
```bash
flask db downgrade
```

## API Endpoints

### List Properties
`GET /api/properties`

Returns a list of properties with basic information.

Response:
```json
[
    {
        "id": 1,
        "price": 350000,
        "status": "for_sale",
        "created_at": "2024-02-16T12:00:00",
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA"
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "property_type": "semi-detached",
            "square_footage": 1200.0
        },
        "features": {
            "has_garden": true,
            "parking_spaces": 2
        },
        "main_image": "https://example.com/image.jpg"
    }
]
```

### Get Property Details
`GET /api/properties/<id>`

Returns detailed information about a specific property.

Response includes additional fields:
- Full property description
- Reception rooms
- EPC rating
- All images including floorplan
- Garden size
- Council tax band
- Key features

### Create Property
`POST /api/properties`

Create a new property listing. Request body should include all required fields.

### Update Property
`PUT /api/properties/<id>`

Update an existing property. Supports partial updates.

### Delete Property
`DELETE /api/properties/<id>`

Remove a property listing.

## Filtering

The list endpoint supports various filters:
- `min_price` & `max_price`
- `bedrooms`
- `property_type`
- `city`
- `min_square_footage`
- `bathrooms`
- `reception_rooms`
- `has_garden`
- `has_garage`
- `epc_rating`
- `ownership_type`
- `postcode_area`

Example: `/api/properties?min_price=300000&bedrooms=3&city=London`

## Development

### Code Style
This project uses the `black` code formatter. To format code:
```bash
black app/ tests/
```

### Continuous Integration
The following checks run on all pull requests:
- Code formatting (black)
- Unit tests (pytest)

### Running Tests
```bash
# Create test database (first time only)
createdb property_db_test

# Run tests
./scripts/run_tests.sh
```

Test coverage includes:
- GET /api/properties endpoint
- GET /api/properties/<id> endpoint
- POST /api/properties endpoint with validation
- PUT /api/properties/<id> endpoint
- DELETE /api/properties/<id> endpoint

## API Examples

### List Properties
```bash
GET /api/properties?min_price=300000&bedrooms=3&city=London
```
Response:
```json
[
    {
        "id": 1,
        "price": 350000,
        "status": "for_sale",
        "created_at": "2024-01-26T17:54:04.872288",
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA"
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "property_type": "semi-detached",
            "square_footage": 1200.0
        },
        "features": {
            "has_garden": true,
            "parking_spaces": 2
        },
        "main_image": "https://maison-property-images.azurewebsites.net/properties/modern-house-1.jpg"
    }
]
```

### Get Property Details
```bash
GET /api/properties/1
```
Response:
```json
{
    "id": 1,
    "price": 350000,
    "status": "for_sale",
    "description": "A lovely 3 bedroom property in London",
    "address": {
        "house_number": "123",
        "street": "Test Street",
        "city": "London",
        "postcode": "SW1 1AA"
    },
    "specs": {
        "bedrooms": 3,
        "bathrooms": 2,
        "reception_rooms": 1,
        "square_footage": 1200.0,
        "property_type": "semi-detached",
        "epc_rating": "B"
    },
    "features": {
        "has_garden": true,
        "garden_size": 100.0,
        "parking_spaces": 2,
        "has_garage": true
    },
    "images": {
        "main": "https://maison-property-images.azurewebsites.net/properties/modern-house-1.jpg",
        "additional": [
            "https://maison-property-images.azurewebsites.net/properties/kitchen-1.jpg",
            "https://maison-property-images.azurewebsites.net/properties/living-room-1.jpg"
        ],
        "floorplan": "https://maison-property-images.azurewebsites.net/floorplans/3-bed-house.pdf"
    }
}
```

### Create Property
```bash
POST /api/properties
Content-Type: application/json

{
    "price": 350000,
    "status": "for_sale",
    "description": "A lovely property",
    "address": {
        "house_number": "123",
        "street": "Test Street",
        "city": "London",
        "postcode": "SW1 1AA"
    },
    "specs": {
        "bedrooms": 3,
        "bathrooms": 2,
        "reception_rooms": 1,
        "square_footage": 1200.0,
        "property_type": "semi-detached",
        "epc_rating": "B"
    },
    "features": {
        "has_garden": true,
        "garden_size": 100.0,
        "parking_spaces": 2,
        "has_garage": true
    }
}
```
Response:
```json
{
    "id": 1
}
```

### Update Property
```bash
PUT /api/properties/1
Content-Type: application/json

{
    "price": 375000,
    "description": "Updated description"
}
```
Response:
```json
{
    "message": "Property updated successfully"
}
```

### Delete Property
```bash
DELETE /api/properties/1
```
Response:
```json
{
    "message": "Property deleted successfully"
}
```