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

# Get all properties including sold and under offer
curl http://localhost:8000/api/properties?include_all=true

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
    "property_id": "123e4567-e89b-12d3-a456-426614174000",
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "main_image_url": "https://example.com/image.jpg",
    "created_at": "2024-02-22T12:00:00Z",
    "seller_id": "3613c096-f41f-479f-a09f-7e0ab53b4eda",
    "status": "for_sale",
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

#### GET /api/properties/<uuid:property_id>
Get details of a specific property

Example:
```bash
curl http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "property_id": "123e4567-e89b-12d3-a456-426614174000",
  "price": 350000,
  "bedrooms": 3,
  "bathrooms": 2,
  "main_image_url": "https://example.com/main.jpg",
  "image_urls": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
  "floorplan_url": "https://example.com/floorplan.jpg",
  "created_at": "2024-02-22T12:00:00Z",
  "last_updated": "2024-02-22T12:00:00Z",
  "seller_id": "3613c096-f41f-479f-a09f-7e0ab53b4eda",
  "status": "for_sale",
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
    "property_id": "123e4567-e89b-12d3-a456-426614174000",
    "price": 350000,
    "bedrooms": 3,
    "bathrooms": 2,
    "main_image_url": "https://example.com/image.jpg",
    "created_at": "2024-02-22T12:00:00Z",
    "seller_id": 1,
    "status": "for_sale",
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
- specs (object with bedrooms, bathrooms, reception_rooms, square_footage, property_type, epc_rating)

Optional fields:
- main_image_url (string)
- images (array of image files, max 5MB each, formats: JPG, JPEG, PNG, GIF)
- details (object with description, property_type, construction_year, parking_spaces, heating_type)
- features (object with has_garden, garden_size, has_garage, parking_spaces)
- media (array of objects with image_url, image_type, display_order)

Example with JSON:
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

Example with images (multipart form data):
```bash
curl -X POST https://maison-api.jollybush-a62cec71.uksouth.azurecontainerapps.io/api/properties \
  -F 'data={
    "price": 350000,
    "user_id": "3613c096-f41f-479f-a09f-7e0ab53b4eda",
    "address": {
      "house_number": "180",
      "street": "Queen's Gate",
      "city": "London",
      "postcode": "SW72AZ"
    },
    "specs": {
      "bedrooms": 5,
      "bathrooms": 3,
      "reception_rooms": 2,
      "square_footage": 2300,
      "property_type": "semi-detached",
      "epc_rating": "A"
    },
    "details": {
      "description": "Beautiful family home",
      "construction_year": 1990,
      "heating_type": "gas central"
    },
    "features": {
      "has_garden": true,
      "garden_size": 100,
      "has_garage": true,
      "parking_spaces": 2
    }
  }' \
  -F "main_image=@/path/to/main-facade.jpg" \
  -F "additional_images=@/path/to/kitchen.jpg" \
  -F "additional_images=@/path/to/living-room.jpg"
```

Response with images:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Property created successfully",
  "warnings": [],
  "image_urls": [
    "https://maisonblobstorage.blob.core.windows.net/property-images/abc123.jpg",
    "https://maisonblobstorage.blob.core.windows.net/property-images/def456.jpg"
  ]
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
Update an existing property

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

### Users

#### GET /api/users
Get a list of all users with their roles and counts

Example:
```bash
curl http://localhost:8000/api/users
```

Response:
```json
{
  "sellers": [
    "3613c096-f41f-479f-a09f-7e0ab53b4eda",
    "4723d197-g52f-580f-b10f-8e0ab53b5fdb"
  ],
  "buyers": [
    "3613c096-f41f-479f-a09f-7e0ab53b4eda",
    "5834e298-h63g-691g-c21g-9f1bc64c6gec",
    "6945f399-i74h-702h-d32h-0g2cd75d7hfd"
  ],
  "counts": {
    "total_buyers": 3,
    "total_sellers": 2
  }
}
```

Note: Some users may appear in both sellers and buyers lists if they have both roles.

Error Response:
```json
{
  "error": "Failed to fetch users"
}
```

#### GET /api/users/{user_id}/dashboard
Get a user's dashboard data including their properties, offers, and saved listings.

Example:
```bash
curl http://localhost:8000/api/users/3613c096-f41f-479f-a09f-7e0ab53b4eda/dashboard
```

Response:
```json
{
  "listed_properties": [],
  "negotiations_as_buyer": [
    {
      "awaiting_response_from": "buyer",
      "buyer_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
      "created_at": "2025-03-02T14:40:59.226953+00:00",
      "current_offer": 360000,
      "last_offer_by": "3613c096-f41f-479f-a09f-7e0ab53b4eda",
      "negotiation_id": "98de7487-c36f-4111-ba80-388f48a1f614",
      "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
      "status": "active",
      "transactions": [
        {
          "created_at": "2025-03-02T14:40:59.240797+00:00",
          "made_by": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
          "offer_amount": 350000,
          "transaction_id": "b8d20daa-0189-4f77-a890-c0347f88ae85"
        },
        {
          "created_at": "2025-03-02T14:45:34.356241+00:00",
          "made_by": "3613c096-f41f-479f-a09f-7e0ab53b4eda",
          "offer_amount": 360000,
          "transaction_id": "e03a6e0d-fb1c-4967-b8ea-e70354f8f7d7"
        }
      ],
      "updated_at": "2025-03-02T14:45:34.345590+00:00"
    }
  ],
  "negotiations_as_seller": [],
  "roles": [
    {
      "role_type": "buyer"
    }
  ],
  "saved_properties": [
    {
      "address": {
        "city": "London",
        "postcode": "SW1 1AA",
        "street": "Sample Street"
      },
      "main_image_url": "https://maisonblobstorage.blob.core.windows.net/property-images/2ea1d64a-18da-4752-9b1e-fa40dccd8da9.jpg",
      "notes": "Great location, need to book viewing",
      "price": 350000,
      "property_id": "5ea12e39-bff9-48e2-b593-eb13b5908959",
      "saved_at": "2025-03-02T12:45:25.214553+00:00",
      "specs": {
        "bathrooms": 2,
        "bedrooms": 3,
        "property_type": "semi-detached"
      },
      "status": "for_sale"
    },
    {
      "address": {
        "city": "Manchester",
        "postcode": "M20 3PS",
        "street": "Oak Avenue"
      },
      "main_image_url": "https://maisonblobstorage.blob.core.windows.net/property-images/2ea1d64a-18da-4752-9b1e-fa40dccd8da9.jpg",
      "notes": "Great location, need to book viewing",
      "price": 425000,
      "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
      "saved_at": "2025-03-02T13:56:00.576177+00:00",
      "specs": {
        "bathrooms": 2,
        "bedrooms": 4,
        "property_type": "detached"
      },
      "status": "for_sale"
    }
  ],
  "total_properties_listed": 0,
  "total_saved_properties": 2,
  "user": {
    "email": "misty16@example.org",
    "first_name": "Wesley",
    "last_name": "Watson",
    "phone_number": "+446479882571",
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6"
  }
}
```

Error Response:
```json
{
  "error": "User not found"
}
```

#### POST /api/users/{user_id}/saved-properties
Save a property for a buyer

Required fields:
- property_id (UUID): The ID of the property to save

Optional fields:
- notes (string): Any notes about the saved property

Example:
```bash
# Save property with notes
curl -X POST http://localhost:8080/api/users/bd70f994-5834-45b9-a6f0-8731e51ff0e6/saved-properties \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "notes": "Great location, need to book viewing"
  }'

# Save property without notes
curl -X POST http://localhost:8080/api/users/bd70f994-5834-45b9-a6f0-8731e51ff0e6/saved-properties \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1"
  }'
```

Response:
```json
{
  "message": "Property saved successfully",
  "saved_property": {
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "notes": "Great location, need to book viewing",  // Will be null if not provided
    "created_at": "2024-02-25T15:30:00Z"
  }
}
```

Error Responses:
```json
{
  "error": "User must be a buyer to save properties"
}
```
```json
{
  "error": "Property already saved"
}
```
```json
{
  "error": "Property not found"
}
```
```json
{
  "error": "property_id is required"
}
```

#### POST /api/users/{user_id}/offers
Create a new offer or counter-offer on a property

Required fields:
- property_id (UUID): The ID of the property
- offer_amount (integer): The amount being offered

Optional fields for counter-offers:
- negotiation_id (UUID): Required when making a counter-offer

Example - New Offer:
```bash
curl -X POST http://localhost:8080/api/users/bd70f994-5834-45b9-a6f0-8731e51ff0e6/offers \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "offer_amount": 350000
  }'
```

Example - Counter Offer:
```bash
curl -X POST http://localhost:8080/api/users/3613c096-f41f-479f-a09f-7e0ab53b4eda/offers \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "offer_amount": 360000,
    "negotiation_id": "98de7487-c36f-4111-ba80-388f48a1f614"
  }'
```

Response:
```json
{
  "message": "Offer submitted successfully",
  "negotiation": {
    "negotiation_id": "789fcdeb-51a2-4bc1-9e8d-326417400000",
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "buyer_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "current_offer": 350000,
    "status": "active",
    "created_at": "2024-02-25T15:30:00Z",
    "last_offer_by": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "awaiting_response_from": "seller"
  }
}
```

Error Responses:
```json
{
  "error": "User must be a buyer to make offers"
}
```
```json
{
  "error": "Cannot make offer on your own property"
}
```
```json
{
  "error": "Active negotiation already exists"
}
```
```json
{
  "error": "Property not found"
}
```
```json
{
  "error": "Unauthorized to make counter-offer"
}
```

#### DELETE /api/users/{user_id}/saved-properties/{property_id}
Remove a property from a buyer's saved properties

Example:
```bash
curl -X DELETE http://localhost:8080/api/users/bd70f994-5834-45b9-a6f0-8731e51ff0e6/saved-properties/fe08df1c-d24e-4f18-9c7b-cfbe842175f1
```

Response:
```json
{
  "message": "Property removed from saved properties",
  "removed_property": {
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1"
  }
}
```

Error Responses:
```json
{
  "error": "User must be a buyer to manage saved properties"
}
```
```json
{
  "error": "Property not found in saved properties"
}
```

#### PATCH /api/users/{user_id}/saved-properties/{property_id}/notes
Update notes for a saved property

Required fields:
- notes (string): The new notes for the saved property

Example:
```bash
curl -X PATCH http://localhost:8080/api/users/bd70f994-5834-45b9-a6f0-8731e51ff0e6/saved-properties/fe08df1c-d24e-4f18-9c7b-cfbe842175f1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Great location, close to schools. Viewing scheduled for next week."
  }'
```

Response:
```json
{
  "message": "Notes updated successfully",
  "saved_property": {
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "property_id": "fe08df1c-d24e-4f18-9c7b-cfbe842175f1",
    "notes": "Great location, close to schools. Viewing scheduled for next week.",
    "updated_at": "2024-02-25T16:30:00Z"
  }
}
```

Error Responses:
```json
{
  "error": "User must be a buyer to update saved properties"
}
```
```json
{
  "error": "Property not found in saved properties"
}
```
```json
{
  "error": "notes field is required"
}
```

#### POST /api/users
Create a new user account

Required fields:
- user_id (UUID): User's Firebase UUID
- first_name (string): User's first name
- last_name (string): User's last name
- email (string): User's email address

Optional fields:
- phone_number (string): User's phone number
- roles (array): User roles (defaults to ["buyer"] if not specified)

Example:
```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "phone_number": "07700900000",
    "roles": [
      {"role_type": "buyer"},
      {"role_type": "seller"}
    ]
  }'
```

Response:
```json
{
  "message": "User created successfully",
  "user": {
    "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "phone_number": "07700900000",
    "roles": [
      {"role_type": "buyer"},
      {"role_type": "seller"}
    ]
  }
}
```

Error Responses:
```json
{
  "error": "Email already registered"
}
```
```json
{
  "error": {
    "email": ["Not a valid email address"],
    "first_name": ["Length must be between 1 and 50"]
  }
}
```

### Offer Management

#### PUT /api/users/{user_id}/offers/{negotiation_id}
Update an offer's status (accept/reject/cancel)

Required fields:
- action (string): Must be one of: "accept", "reject", "cancel"

Rules:
- Only the buyer or seller involved in the negotiation can update its status
- Can only accept/reject offers made by the other party
- Can only cancel your own most recent offer
- If buyer cancels their first offer, the entire negotiation is cancelled
- If cancelling a counter-offer, reverts to the previous offer from the other party

Examples:
```bash
# Accept an offer
curl -X PUT http://localhost:8000/api/users/seller_id/offers/negotiation_id \
  -H "Content-Type: application/json" \
  -d '{
    "action": "accept"
  }'

# Reject an offer
curl -X PUT http://localhost:8000/api/users/seller_id/offers/negotiation_id \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject"
  }'

# Cancel your offer/counter-offer
curl -X PUT http://localhost:8000/api/users/user_id/offers/negotiation_id \
  -H "Content-Type: application/json" \
  -d '{
    "action": "cancel"
  }'
```

Response:
```json
{
  "message": "Counter-offer cancelled, reverted to previous offer",
  "negotiation": {
    "negotiation_id": "123e4567-e89b-12d3-a456-426614174000",
    "property_id": "123e4567-e89b-12d3-a456-426614174001",
    "buyer_id": "123e4567-e89b-12d3-a456-426614174002",
    "seller_id": "123e4567-e89b-12d3-a456-426614174003",
    "current_offer_amount": 350000,
    "status": "active",
    "updated_at": "2024-02-22T12:00:00Z",
    "action_by": "123e4567-e89b-12d3-a456-426614174002",
    "property_status": "for_sale",
    "last_offer_by": "123e4567-e89b-12d3-a456-426614174002"
  }
}
```

Error Responses:
```json
{
  "error": "Cannot accept/reject your own offer. Waiting for buyer response"
}
```
```json
{
  "error": "Can only cancel your own most recent offer"
}
```
```json
{
  "error": "Cannot update: negotiation is already accepted"
}
```

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| include_all | bool | Include all properties regardless of status | ?include_all=true |
| min_price | int | Minimum price | ?min_price=200000 |
| max_price | int | Maximum price | ?max_price=500000 |
| bedrooms | int | Number of bedrooms | ?bedrooms=3 |
| bathrooms | int | Number of bathrooms | ?bathrooms=2 |
| city | string | City location | ?city=London |
| property_type | string | Type of property | ?property_type=semi-detached |
| has_garden | bool | Has garden | ?has_garden=true |
| parking_spaces | int | Minimum parking spaces | ?parking_spaces=2 |
| status | string | Property status | ?status=for_sale |

### Property Status Updates

Properties can have one of three statuses: `for_sale`, `under_offer`, or `sold`. Status transitions follow these rules:

- From `for_sale`: Can transition to `under_offer` or `sold`
- From `under_offer`: Can transition back to `for_sale` or to `sold`
- From `sold`: Cannot transition to any other status

#### Update Property Status

```bash
# Mark property as under offer
curl -X PUT http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "under_offer"
  }'

# Mark property as sold
curl -X PUT http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "sold"
  }'

# Return property to for_sale (only valid from under_offer)
curl -X PUT http://localhost:8000/api/properties/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "for_sale"
  }'
```

Response:
```json
{
  "message": "Property updated successfully",
  "status": "under_offer"
}
```

Error Response (Invalid Status):
```json
{
  "error": "Invalid status transition from for_sale to sold"
}
```

Error Response (Updating Sold Property):
```json
{
  "error": "Cannot update status of sold property"
}
```

#### Filter Properties by Status

```bash
# Get only properties for sale (default behavior)
curl http://localhost:8000/api/properties

# Get properties under offer
curl http://localhost:8000/api/properties?status=under_offer

# Get sold properties
curl http://localhost:8000/api/properties?status=sold

# Get all properties regardless of status
curl http://localhost:8000/api/properties?include_all=true
```

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

6. **Azure Blob Storage Integration**
   - Property images now stored in Azure Blob Storage
   - Automatic image cleanup when properties are deleted
   - Support for multiple image uploads
   - Image validation (size, format, dimensions)

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

## Azure Container App Configuration

### Setting Environment Variables and Secrets

1. Set basic environment variables:
```bash
az containerapp update -n maison-api -g maison-rg \
  --set-env-vars \
  DATABASE_URL="postgresql://maisondbadmin:password@maison-db.postgres.database.azure.com/property_db?sslmode=require" \
  FLASK_APP="wsgi.py" \
  FLASK_ENV="production"
```

2. Set the Azure Storage secret:
```bash
az containerapp secret set -n maison-api -g maison-rg \
  --secrets azure-storage-connection="your-connection-string"
```