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

A RESTful API for managing property listings.

## API Endpoints

### 1. List Properties (GET /api/properties)
Retrieves a list of properties with optional filtering.

```bash
# Get all properties
curl https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties

# Filter by price range
curl https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties?min_price=200000&max_price=500000

# Filter by location
curl https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties?city=London

# Filter by features
curl https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties?bedrooms=3&bathrooms=2

# Example Response
{
    "properties": [
        {
            "id": 1,
            "price": 350000,
            "bedrooms": 3,
            "bathrooms": 2,
            "main_image_url": "https://example.com/image.jpg",
            "address": {
                "city": "London",
                "postcode": "SW1A 1AA"
            },
            "features": {
                "has_garden": true,
                "parking_spaces": 2
            }
        }
    ]
}
```

### 2. Get Property Details (GET /api/properties/{id})
Retrieves detailed information about a specific property.

```bash
# Get property with ID 1
curl https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties/1

# Example Response
{
    "id": 1,
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "main_image_url": "https://example.com/image.jpg",
    "address": {
        "house_number": "42",
        "street": "High Street",
        "city": "London",
        "postcode": "SW1A 1AA"
    },
    "specs": {
        "square_footage": 1200,
        "property_type": "semi-detached",
        "epc_rating": "B"
    },
    "features": {
        "has_garden": true,
        "garden_size": 100,
        "parking_spaces": 2,
        "has_garage": true
    },
    "details": {
        "description": "Beautiful family home...",
        "construction_year": 2010
    },
    "media": [
        {
            "image_url": "https://example.com/image1.jpg",
            "image_type": "additional"
        }
    ]
}
```

### 3. Create Property (POST /api/properties)
Creates a new property listing.

```bash
# Create new property
curl -X POST https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties \
  -H "Content-Type: application/json" \
  -d '{
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "address": {
        "house_number": "42",
        "street": "High Street",
        "city": "London",
        "postcode": "SW1A 1AA"
    },
    "specs": {
        "square_footage": 1200,
        "property_type": "semi-detached",
        "epc_rating": "B"
    }
  }'

# Example Response
{
    "id": 1,
    "message": "Property created successfully"
}
```

### 4. Update Property (PUT /api/properties/{id})
Updates an existing property listing.

```bash
# Update property with ID 1
curl -X PUT https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 375000,
    "features": {
        "has_garden": true,
        "parking_spaces": 2
    }
  }'

# Example Response
{
    "message": "Property updated successfully"
}
```

### 5. Delete Property (DELETE /api/properties/{id})
Removes a property listing.

```bash
# Delete property with ID 1
curl -X DELETE https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties/1

# Example Response
{
    "message": "Property deleted successfully"
}
```

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| min_price | int | Minimum price | ?min_price=200000 |
| max_price | int | Maximum price | ?max_price=500000 |
| bedrooms | int | Number of bedrooms | ?bedrooms=3 |
| bathrooms | int | Number of bathrooms | ?bathrooms=2 |
| city | string | City location | ?city=London |
| property_type | string | Type of property | ?property_type=semi-detached |
| has_garden | bool | Has garden | ?has_garden=true |
| parking_spaces | int | Minimum parking spaces | ?parking_spaces=2 |

## Setup

### Requirements
+ - Python 3.11.7
  - PostgreSQL 14+

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