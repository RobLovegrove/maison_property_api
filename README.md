<style>
.highlight pre {
  color: #ffffff !important;
}
pre code {
  color: #ffffff !important;
}
code {
  color: #ffffff !important;
}
</style>

# MaiSON Property API

A Flask-based REST API powering the MaiSON real estate platform.

## API Endpoints

### Examples

#### Using curl

List all properties:
```bash
curl http://localhost:8080/api/properties
```

Get a specific property:
```bash
curl http://localhost:8080/api/properties/1
```

Create a new property:
```bash
curl -X POST http://localhost:8080/api/properties \
  -H "Content-Type: application/json" \
  -d '{
    "price": 350000,
    "address": {
      "house_number": "42",
      "street": "Example Street",
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
    "details": {
      "description": "A lovely property...",
      "property_type": "semi-detached",
      "construction_year": 2020,
      "parking_spaces": 2,
      "heating_type": "gas"
    }
  }'
```

Update a property:
```bash
curl -X PUT http://localhost:8080/api/properties/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 375000,
    "specs": {
      "bedrooms": 4,
      "bathrooms": 2,
      "reception_rooms": 2,
      "square_footage": 1500.0,
      "property_type": "semi-detached",
      "epc_rating": "A"
    }
  }'
```

Delete a property:
```bash
curl -X DELETE http://localhost:8080/api/properties/1
```

Filter properties:
```bash
# Properties over £400,000
curl "http://localhost:8080/api/properties?min_price=400000"

# Properties with 3+ bedrooms
curl "http://localhost:8080/api/properties?bedrooms=3"

# Properties in London with gardens
curl "http://localhost:8080/api/properties?city=London&has_garden=true"
```

#### Using Python requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8080"

# List all properties
response = requests.get(f"{BASE_URL}/api/properties")
properties = response.json()

# Get specific property
property_id = 1
response = requests.get(f"{BASE_URL}/api/properties/{property_id}")
property_detail = response.json()

# Create new property
new_property = {
    "price": 350000,
    "address": {
        "house_number": "42",
        "street": "Example Street",
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
    "details": {
        "description": "A lovely property...",
        "property_type": "semi-detached",
        "construction_year": 2020,
        "parking_spaces": 2,
        "heating_type": "gas"
    }
}
response = requests.post(f"{BASE_URL}/api/properties", json=new_property)
created_property = response.json()

# Update property
update_data = {
    "price": 375000,
    "specs": {
        "bedrooms": 4,
        "bathrooms": 2,
        "reception_rooms": 2,
        "square_footage": 1500.0,
        "property_type": "semi-detached",
        "epc_rating": "A"
    }
}
response = requests.put(f"{BASE_URL}/api/properties/{property_id}", json=update_data)

# Delete property
response = requests.delete(f"{BASE_URL}/api/properties/{property_id}")

# Filter properties
params = {
    'min_price': 400000,
    'bedrooms': 3,
    'city': 'London',
    'has_garden': True
}
response = requests.get(f"{BASE_URL}/api/properties", params=params)
filtered_properties = response.json()
```

### List Properties
`GET /api/properties`

Query Parameters:
- `min_price`: Minimum price (integer)
- `bedrooms`: Minimum number of bedrooms (integer)
- `bathrooms`: Minimum number of bathrooms (integer)
- `city`: City name (string)
- `has_garden`: Filter for properties with gardens (boolean)
- `has_garage`: Filter for properties with garages (boolean)
- `min_square_footage`: Minimum square footage (float)

Returns a list of properties with basic information.

Response:
```
[
    {
        "id": 1,
        "price": 350000,
        "bedrooms": 3,
        "bathrooms": 2,
        "main_image_url": "https://example.com/image.jpg",
        "created_at": "2024-02-16T12:00:00",
        "address": {
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA"
        },
        "specs": {
            "property_type": "semi-detached",
            "square_footage": 1200.0
        }
    }
]
```

### Get Property Details
`GET /api/properties/<id>`

Returns detailed information about a specific property.

Response:
```
{
    "id": 1,
    "price": 350000,
    "created_at": "2024-02-16T12:00:00",
    "images": {
        "main": "https://example.com/main.jpg",
        "additional": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ],
        "floorplan": "https://example.com/floorplan.pdf"
    },
    "address": {
        "house_number": "123",
        "street": "Test Street",
        "city": "London",
        "postcode": "SW1 1AA",
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    "specs": {
        "bedrooms": 3,
        "bathrooms": 2,
        "reception_rooms": 2,
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
    "details": {
        "description": "A stunning 3 bedroom property...",
        "property_type": "semi-detached",
        "construction_year": 1990,
        "parking_spaces": 2,
        "heating_type": "Gas Central"
    }
}
```

## Setup

### Database Setup

1. Create a local test database (for running tests):
```
createdb maison_test
```

2. Create a `.env` file with your Azure database credentials:
```
# .env
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

Note: Contact the team for the actual database credentials. Never commit the `.env` file to version control.

3. Initialize database schema:
```
flask db upgrade
```

### Running the API

1. Start the API server (uses Azure database):
```
./scripts/run.sh
```

The API will be available at `http://localhost:8080`

### Testing

Run the test suite (uses local test database):
```
./scripts/setup_test_db.sh
```

Or run specific tests:
```
pytest tests/test_properties.py
```

### Database Structure

The database consists of several related tables:
- `properties`: Core property information
- `addresses`: Property location details
- `property_specs`: Property specifications
- `property_features`: Additional property features
- `property_details`: Detailed property information
- `property_media`: Property images and floorplans

## API Response Codes

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input provided
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a message:
```json
{
    "error": "Detailed error message"
}
```