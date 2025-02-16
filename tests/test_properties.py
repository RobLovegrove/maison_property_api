import pytest
from app.models import Property
from datetime import datetime  # noqa: F401


@pytest.fixture
def sample_property():
    return {
        "price": 350000,
        "status": "for_sale",
        "description": "A lovely property",
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA",
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "reception_rooms": 1,
            "square_footage": 1200.0,
            "property_type": "semi-detached",
            "epc_rating": "B",
        },
        "features": {
            "has_garden": True,
            "garden_size": 100.0,
            "parking_spaces": 2,
            "has_garage": True,
        },
        "ownership_type": "freehold",
        "key_features": ["Garden"],
        "council_tax_band": "C",
    }


def test_get_properties_empty(client, session, app_context):
    """Test GET /api/properties returns empty list when no properties exist"""
    # Clear the database using the session
    session.query(Property).delete()
    session.commit()

    response = client.get("/api/properties")
    assert response.status_code == 200
    assert response.json == []


def test_create_property(client, session, sample_property):
    """Test POST /api/properties creates a new property with related data"""
    response = client.post("/api/properties", json=sample_property)
    assert response.status_code == 201
    assert "id" in response.json

    # Verify property was created with all related data
    get_response = client.get(f'/api/properties/{response.json["id"]}')
    assert get_response.status_code == 200
    data = get_response.json

    assert data["price"] == sample_property["price"]
    assert data["address"]["street"] == (sample_property["address"]["street"])
    assert data["specs"]["bedrooms"] == (sample_property["specs"]["bedrooms"])


def test_get_property_detail(client, session, sample_property):
    """Test GET /api/properties/<id> returns detailed property information"""
    # Create property first
    create_response = client.post("/api/properties", json=sample_property)
    property_id = create_response.json["id"]

    # Get property details
    response = client.get(f"/api/properties/{property_id}")
    assert response.status_code == 200
    data = response.json

    # Verify nested data structures
    assert data["address"]["street"] == (sample_property["address"]["street"])
    assert data["specs"]["bedrooms"] == (sample_property["specs"]["bedrooms"])
    assert data["features"]["has_garden"] == (
        sample_property["features"]["has_garden"]
    )


def test_update_property(client, session, app_context, sample_property):
    """Test PUT /api/properties/<id> updates property information"""
    # Create property first
    create_response = client.post("/api/properties", json=sample_property)
    assert create_response.status_code == 201
    property_id = create_response.json["id"]

    # Update property
    update_data = {
        "price": 375000,
        "description": "Updated description",
        "specs": {"bedrooms": 4},
        "address": {"postcode": "SW1 2BB"},
    }
    response = client.put(f"/api/properties/{property_id}", json=update_data)
    assert response.status_code == 200

    # Verify update
    get_response = client.get(f"/api/properties/{property_id}")
    data = get_response.json
    assert data["price"] == 375000
    assert data["specs"]["bedrooms"] == 4
    assert data["address"]["postcode"] == "SW1 2BB"


def test_delete_property(client, session, app_context, sample_property):
    """Test DELETE /api/properties/<id> removes the property"""
    # Create property first
    create_response = client.post("/api/properties", json=sample_property)
    assert create_response.status_code == 201
    property_id = create_response.json["id"]

    # Delete property
    response = client.delete(f"/api/properties/{property_id}")
    assert response.status_code == 200

    # Verify deletion
    get_response = client.get(f"/api/properties/{property_id}")
    assert get_response.status_code == 404


def test_create_property_validation(client):
    """Test POST /api/properties validates required fields"""
    invalid_property = {
        "price": "not a number",
        "address": {
            "house_number": 123,  # Should be string
            "city": None,  # Required field
        },
    }
    response = client.post("/api/properties", json=invalid_property)
    assert response.status_code == 400
    assert "errors" in response.json


def test_filter_properties(client, session, app_context):
    """Test GET /api/properties with filters"""
    properties = [
        {
            "price": 350000,
            "status": "for_sale",
            "description": "Property 1",
            "address": {
                "house_number": "123",
                "street": "Test Street",
                "city": "London",
                "postcode": "SW1 1AA",
            },
            "specs": {
                "bedrooms": 3,
                "bathrooms": 2,
                "reception_rooms": 1,
                "square_footage": 1200.0,
                "property_type": "semi-detached",
                "epc_rating": "B",
            },
            "features": {
                "has_garden": True,
                "garden_size": 100.0,
                "parking_spaces": 1,
                "has_garage": False,
            },
            "ownership_type": "freehold",
            "key_features": ["Garden"],
            "council_tax_band": "C",
        },
        {
            "price": 500000,
            "status": "for_sale",
            "description": "Property 2",
            "address": {
                "house_number": "456",
                "street": "Other Street",
                "city": "Manchester",
                "postcode": "M1 1AA",
            },
            "specs": {
                "bedrooms": 4,
                "bathrooms": 3,
                "reception_rooms": 2,
                "square_footage": 1500.0,
                "property_type": "detached",
                "epc_rating": "A",
            },
            "features": {
                "has_garden": True,
                "parking_spaces": 2,
                "has_garage": True,
            },
            "ownership_type": "freehold",
            "key_features": ["Garage"],
            "council_tax_band": "D",
        },
    ]

    # Create properties
    for prop in properties:
        client.post("/api/properties", json=prop)

    # Test price filter
    response = client.get("/api/properties?min_price=400000")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["price"] == 500000

    # Test bedrooms filter
    response = client.get("/api/properties?bedrooms=4")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["specs"]["bedrooms"] == 4

    # Test city filter
    response = client.get("/api/properties?city=London")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["address"]["city"] == "London"


def test_advanced_filters(client, session, app_context):
    """Test advanced property filters"""
    property_data = {
        "price": 450000,
        "status": "for_sale",
        "description": "Test Property",
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA",
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "reception_rooms": 2,
            "square_footage": 1500.0,
            "property_type": "detached",
            "epc_rating": "A",
        },
        "features": {
            "has_garden": True,
            "garden_size": 100.0,
            "parking_spaces": 2,
            "has_garage": True,
        },
        "ownership_type": "freehold",
    }

    client.post("/api/properties", json=property_data)

    # Test various filter combinations
    filters = [
        ("min_square_footage=1400", 1),  # >= 1400 sq ft
        ("bathrooms=2&has_garage=true", 1),  # 2+ baths
        ("epc_rating=A&has_garden=true", 1),  # A-rated
        ("postcode_area=SW1", 1),  # SW1 area
        ("min_square_footage=2000", 0),  # None this large
    ]

    for filter_str, expected_count in filters:
        response = client.get(f"/api/properties?{filter_str}")
        assert response.status_code == 200
        assert len(response.json) == expected_count


def test_properties_default_ordering(client, session, app_context):
    """Test properties ordered by created_at and id when timestamps match"""
    # Define test properties
    properties = [
        {
            "price": 350000,
            "status": "for_sale",
            "description": "First Property",
            "address": {
                "house_number": "123",
                "street": "Test Street",
                "city": "London",
                "postcode": "SW1 1AA",
            },
            "specs": {
                "bedrooms": 2,
                "bathrooms": 1,
                "reception_rooms": 1,
                "square_footage": 800.0,
                "property_type": "flat",
                "epc_rating": "B",
            },
            "features": {
                "has_garden": False,
                "parking_spaces": 0,
                "has_garage": False,
            },
            "ownership_type": "freehold",
            "key_features": [],
            "council_tax_band": "B",
        },
        {
            "price": 750000,
            "status": "for_sale",
            "description": "Second Property",
            "address": {
                "house_number": "456",
                "street": "Other Street",
                "city": "Manchester",
                "postcode": "M1 1AA",
            },
            "specs": {
                "bedrooms": 4,
                "bathrooms": 2,
                "reception_rooms": 2,
                "square_footage": 1500.0,
                "property_type": "detached",
                "epc_rating": "A",
            },
            "features": {
                "has_garden": True,
                "parking_spaces": 2,
                "has_garage": True,
            },
            "ownership_type": "freehold",
            "key_features": ["Garage", "Garden"],
            "council_tax_band": "E",
        },
    ]

    # Create two properties with the same timestamp
    prop1 = client.post("/api/properties", json=properties[0])
    prop2 = client.post("/api/properties", json=properties[1])
    assert prop1.status_code == 201
    assert prop2.status_code == 201

    # Get and verify ordering
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert len(response.json) == 2

    print("\nResponse order:")
    for idx, prop in enumerate(response.json):
        print(
            f"Property {idx}: {prop['description']} "
            f"(created: {prop['created_at']}, id: {prop['id']})"
        )

    # Properties with same timestamp should be ordered by ID (newest first)
    assert response.json[0]["id"] > response.json[1]["id"]
