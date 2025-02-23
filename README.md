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

# Maison Property API

## Database Configuration
The API uses PostgreSQL database named 'property_db' hosted on Azure.

# Properties API

A Flask-based REST API for managing property listings.

## API Endpoints

### Properties

#### GET /api/properties
Get a list of all properties

Example:
```bash
# Get all properties
curl http://localhost:8000/api/properties

# Filter properties
curl http://localhost:8000/api/properties?min_price=350000
curl http://localhost:8000/api/properties?property_type=semi-detached
curl http://localhost:8000/api/properties?min_bedrooms=3
curl http://localhost:8000/api/properties?postcode=SW1
```

Response:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "main_image_url": "https://example.com/image.jpg",
    "created_at": "2024-02-22T12:00:00Z",
    "owner_id": 1,
    "address": {
      "street": "Sample Street",
      "city": "London",
      "postcode": "SW1 1AA"
    },
    "specs": {
      "property_type": "semi-detached",
      "square_footage": 1200.0
    }
  },
  // ... more properties
]
```

Error Response (User not found):
```json
{
  "error": "User not found"
}
```

#### GET /api/properties/<uuid:property_id>
Get details of a specific property (Public - No auth required)

Example:
```bash
curl http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "price": 350000,
  "bedrooms": 3,
  "bathrooms": 2,
  "main_image_url": "https://example.com/main.jpg",
  "image_urls": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
  "floorplan_url": "https://example.com/floorplan.jpg",
  "created_at": "2024-02-22T12:00:00Z",
  "last_updated": "2024-02-22T12:00:00Z",
  "owner_id": 1,
  "address": {
    "house_number": "123",
    "street": "Sample Street",
    "city": "London",
    "postcode": "SW1 1AA",
    "latitude": 51.5074,
    "longitude": -0.1278
  },
  "specs": {
    "bedrooms": 3,
    "bathrooms": 2,
    "reception_rooms": 2,
    "square_footage": 1200.5,
    "property_type": "semi-detached",
    "epc_rating": "B"
  },
  "details": {
    "description": "Beautiful family home",
    "property_type": "residential",
    "construction_year": 1990,
    "parking_spaces": 2,
    "heating_type": "gas central"
  },
  "features": {
    "has_garden": true,
    "garden_size": 100.5,
    "has_garage": true,
    "parking_spaces": 2
  }
}
```

Error Response:
```json
{
  "error": "Property not found"
}
```

#### GET /api/properties/user/{user_id}
Get all properties for a specific user

Example:
```bash
curl http://localhost:8000/api/properties/user/1
```

Response:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "main_image_url": "https://example.com/image.jpg",
    "created_at": "2024-02-22T12:00:00Z",
    "owner_id": 1,
    "address": {
      "street": "Sample Street",
      "city": "London",
      "postcode": "SW1 1AA"
    },
    "specs": {
      "property_type": "semi-detached",
      "square_footage": 1200.0
    }
  },
  // ... more properties owned by user 1
]
```

Error Response (User not found):
```json
{
  "error": "User not found"
}
```

#### POST /api/properties
Create a new property listing

Required fields:
- price (integer)
- user_id (integer)
- address (object with house_number, street, city, postcode)
- specs (object with bedrooms, bathrooms, reception_rooms, square_footage, 
  property_type, epc_rating)

Optional fields:
- main_image_url (string)
- details (object with description, property_type, construction_year, 
  parking_spaces, heating_type)
- features (object with has_garden, garden_size, has_garage, parking_spaces)
- media (array of objects with image_url, image_type, display_order)

Example:
```bash
curl -X POST http://localhost:8000/api/properties \
  -H "Content-Type: application/json" \
  -d '{
    "price": 350000,
    "user_id": 1,
    "main_image_url": "https://example.com/main.jpg",
    "address": {
      "house_number": "123",
      "street": "Sample Street",
      "city": "London",
      "postcode": "SW1 1AA"
    },
    "specs": {
      "bedrooms": 3,
      "bathrooms": 2,
      "reception_rooms": 2,
      "square_footage": 1200.5,
      "property_type": "semi-detached",
      "epc_rating": "B"
    },
    "details": {
      "description": "Beautiful family home",
      "property_type": "residential",
      "construction_year": 1990,
      "parking_spaces": 2,
      "heating_type": "gas central"
    },
    "features": {
      "has_garden": true,
      "garden_size": 100.5,
      "has_garage": true,
      "parking_spaces": 2
    },
    "media": [
      {
        "image_url": "https://example.com/img1.jpg",
        "image_type": "interior",
        "display_order": 1
      }
    ]
  }'
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Property created successfully",
  "warnings": []
}
```

Error Response:
```json
{
  "errors": [
    "Price must be a positive number",
    "Address street is required"
  ]
}
```

#### PUT /api/properties/<uuid:property_id>
Update an existing property (Protected - Requires authentication)

Example:
```bash
curl -X PUT http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${FIREBASE_ID_TOKEN}" \
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

Response:
```json
{
  "message": "Property updated successfully"
}
```

Error Response:
```json
{
  "error": "Property not found"
}
```

#### DELETE /api/properties/<uuid:property_id>
Delete a property (Protected - Requires authentication)

Example:
```bash
curl -X DELETE http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer ${FIREBASE_ID_TOKEN}"
```

Response:
```json
{
  "message": "Property deleted successfully"
}
```

Error Response:
```json
{
  "error": "Property not found"
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

## Recent Updates

1. **UUID Implementation**
   - Properties now use UUID primary keys instead of sequential integers
   - All property references use UUIDs for better scalability

2. **Enhanced Validation**
   - Added Marshmallow schemas for request validation
   - Improved error messages and validation feedback

3. **Geocoding Support**
   - Automatic geocoding of property addresses
   - Latitude/longitude added to address records
   - Graceful handling of geocoding failures

4. **Required User Association**
   - Properties must now be associated with a user
   - User ID required for property creation

5. **Error Handling**
   - Comprehensive error handling for all endpoints
   - Detailed error messages and appropriate HTTP status codes
   - Warning messages for non-fatal issues

## Setup

### Requirements
- Python 3.11.7
- PostgreSQL 14+
- Required Python packages in requirements.txt

### Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
flask db upgrade
```

### Running Tests
```bash
pytest tests/
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

## Running Locally

1. Build the Docker image:
```bash
docker build -t maison_property_api .
```

2. Run the container:
```bash
docker run -d \
  -p 8000:8080 \
  -e DATABASE_URL="your_database_url" \
  -e FLASK_APP="wsgi.py" \
  -e FLASK_ENV="production" \
  --name maison_api \
  maison_property_api
```

3. Test the API:
```bash
curl http://localhost:8000/health
```

## Error Responses

# No error responses currently documented