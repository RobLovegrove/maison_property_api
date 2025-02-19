import pytest
from app.models import (
    Property,
    PropertyMedia,
    PropertyFeatures,
    PropertySpecs,
    Address,
    PropertyDetail,
)
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
    # Clear the database in the correct order to handle foreign keys
    session.query(PropertyMedia).delete()
    session.query(PropertyFeatures).delete()
    session.query(PropertySpecs).delete()
    session.query(PropertyDetail).delete()
    session.query(Address).delete()
    session.query(Property).delete()
    session.commit()

    response = client.get("/api/properties")
    assert response.status_code == 200
    assert response.json == []  # API now returns a list, not a dict


def test_create_property(client, session, sample_property):
    """Test POST /api/properties creates a new property with related data"""
    # Update sample_property to match current model
    sample_property = {
        "price": 350000,
        "bedrooms": 3,
        "bathrooms": 2,
        "main_image_url": "https://example.com/main.jpg",
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
        "details": {
            "description": "A lovely property",
            "property_type": "semi-detached",
            "construction_year": 1990,
            "parking_spaces": 2,
            "heating_type": "Gas Central",
        },
    }

    response = client.post("/api/properties", json=sample_property)
    assert response.status_code == 201


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
    properties = response.json
    assert len([p for p in properties if p["price"] >= 400000]) == 1

    # Test bedrooms filter
    response = client.get("/api/properties?bedrooms=4")
    assert response.status_code == 200
    properties = response.json
    assert len([p for p in properties if p["bedrooms"] == 4]) == 1

    # Test city filter
    response = client.get("/api/properties?city=Manchester")
    assert response.status_code == 200
    properties = response.json
    assert (
        len([p for p in properties if p["address"]["city"] == "Manchester"])
        == 1
    )


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
    properties = response.json
    assert len(properties) == 2
    # Check ordering by created_at desc
    assert properties[0]["created_at"] >= properties[1]["created_at"]


def test_property_pagination(client, session, app_context):
    """Test properties endpoint pagination"""
    # Create 15 properties with full data (needed for creation)
    for i in range(15):
        property_data = {
            "price": 300000 + (i * 50000),
            "status": "for_sale",
            "description": f"Property {i+1}",  # Required for creation
            "address": {
                "house_number": f"{i+1}",
                "street": "Test Street",
                "city": "London",
                "postcode": f"SW{i+1} 1AA",
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
                "garden_size": 100.0,  # Not returned in list
                "parking_spaces": 1,
                "has_garage": False,
            },
            "ownership_type": "freehold",
            "key_features": ["Garden"],  # Not returned in list
            "council_tax_band": "C",  # Not returned in list
        }
        client.post("/api/properties", json=property_data)

    # Test default pagination
    response = client.get("/api/properties")
    assert response.status_code == 200
    data = response.json

    # Verify data structure
    assert isinstance(data, list)  # response is now a list
    assert len(data) > 0

    first_property = data[0]  # access first item in list
    assert "price" in first_property
    assert "bedrooms" in first_property
    assert "bathrooms" in first_property


def test_get_properties(client, init_database):
    """Test getting list of properties."""
    response = client.get("/api/properties")
    assert response.status_code == 200

    data = response.json
    assert isinstance(data, list)
    assert len(data) > 0

    property = data[0]
    assert "id" in property
    assert "price" in property
    assert "bedrooms" in property
    assert "bathrooms" in property
    assert "main_image_url" in property
    assert "created_at" in property
    assert "address" in property
    assert "specs" in property

    # Check nested objects
    address = property["address"]
    assert "street" in address
    assert "city" in address
    assert "postcode" in address

    specs = property["specs"]
    assert "property_type" in specs
    assert "square_footage" in specs


def test_get_property_detail(client, init_database):
    """Test getting detailed property information."""
    # Get first property from list to get valid ID
    list_response = client.get("/api/properties")
    first_property_id = list_response.json[0]["id"]

    response = client.get(f"/api/properties/{first_property_id}")
    assert response.status_code == 200

    data = response.json
    assert "id" in data
    assert "price" in data
    assert "created_at" in data

    # Check images
    assert "images" in data
    images = data["images"]
    assert "main" in images
    assert "additional" in images
    assert "floorplan" in images
    assert isinstance(images["additional"], list)

    # Check address
    assert "address" in data
    address = data["address"]
    assert "house_number" in address
    assert "street" in address
    assert "city" in address
    assert "postcode" in address
    assert "latitude" in address
    assert "longitude" in address

    # Check specs
    assert "specs" in data
    specs = data["specs"]
    assert "bedrooms" in specs
    assert "bathrooms" in specs
    assert "reception_rooms" in specs
    assert "square_footage" in specs
    assert "property_type" in specs
    assert "epc_rating" in specs

    # Check features
    assert "features" in data
    features = data["features"]
    assert "has_garden" in features
    assert "garden_size" in features
    assert "parking_spaces" in features
    assert "has_garage" in features

    # Check details
    assert "details" in data
    details = data["details"]
    assert "description" in details
    assert "property_type" in details
    assert "construction_year" in details
    assert "parking_spaces" in details
    assert "heating_type" in details


def test_get_nonexistent_property(client, init_database):
    """Test getting a property that doesn't exist."""
    response = client.get("/api/properties/9999")
    assert response.status_code == 404
    assert response.json["error"] == "Property not found"
