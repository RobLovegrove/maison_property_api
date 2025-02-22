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

# Properties API

A Flask-based REST API for managing property listings.

## API Endpoints

### Properties

#### GET /api/properties
Get a list of all properties
- Optional query parameters for filtering:
  - min_price
  - max_price
  - property_type
  - min_bedrooms
  - postcode

#### GET /api/properties/<uuid:property_id>
Get details of a specific property
- Returns property details including owner_id, address, and specifications
- Returns 404 if property not found

#### GET /api/properties/user/<int:user_id>
Get all properties for a specific user
- Returns array of properties owned by the user
- Returns 404 if user not found

#### POST /api/properties
Create a new property listing
- Required fields in request body:
  - price (integer)
  - user_id (integer)
  - address (object)
  - specs (object)
- Optional fields:
  - features (object)
  - details (object)
  - media (array)

#### PUT /api/properties/<uuid:property_id>
Update an existing property
- Any fields from the POST schema can be updated
- Returns 404 if property not found

#### DELETE /api/properties/<uuid:property_id>
Delete a property
- Returns 404 if property not found

### Response Format Example

```json
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