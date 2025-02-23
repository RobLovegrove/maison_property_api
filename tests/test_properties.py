import pytest
from app.models import Property  # Add this import
from datetime import datetime, UTC
from uuid import uuid4


@pytest.fixture
def test_property_data(test_user):
    """Valid property data for tests."""
    return {
        "price": 350000,
        "user_id": test_user.id,
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "reception_rooms": 1,
            "square_footage": 1200.0,
            "property_type": "semi-detached",
            "epc_rating": "B",
        },
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA",
        },
    }


def test_get_properties_empty(client, session):
    """Test GET /api/properties returns empty list when no properties exist"""
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert response.json == []


def test_create_property(client, test_property_data):
    """Test creating a property."""
    response = client.post("/api/properties", json=test_property_data)
    assert response.status_code == 201
    assert "id" in response.json
    assert response.json["message"] == "Property created successfully"


def test_get_property_detail(client, init_database):
    """Test getting a single property with all details."""
    property = init_database
    response = client.get(f"/api/properties/{property.id}")
    assert response.status_code == 200
    data = response.json

    # Update the expected image URL
    expected_image_url = (
        "https://maisonblobstorage.blob.core.windows.net/"
        "property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
    )
    assert data["main_image_url"] == expected_image_url
    assert data["price"] == 350000
    assert data["bedrooms"] == 3
    assert data["bathrooms"] == 2
    assert data["address"]["street"] == "Test Street"
    assert data["specs"]["property_type"] == "semi-detached"


def test_get_property_without_media(client, test_user, session):
    """Test getting property without any media."""
    property = Property(
        id=uuid4(),
        price=350000,
        bedrooms=3,
        bathrooms=2.0,
        user_id=test_user.id,
        created_at=datetime.now(UTC),
    )
    session.add(property)
    session.commit()

    response = client.get(f"/api/properties/{property.id}")
    assert response.status_code == 200
    data = response.json

    assert data["main_image_url"] is None
    assert data["image_urls"] == []
    assert data["floorplan_url"] is None


def test_get_nonexistent_property(client, session):
    """Test getting a property that doesn't exist."""
    response = client.get(
        "/api/properties/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
    assert response.json["error"] == "Property not found"


def test_update_property(client, init_database):
    """Test updating a property."""
    update_data = {"price": 375000, "specs": {"bedrooms": 4, "bathrooms": 2}}

    response = client.put(
        f"/api/properties/{init_database.id}", json=update_data
    )
    assert response.status_code == 200
    assert response.json["message"] == "Property updated successfully"


def test_delete_property(client, init_database):
    """Test deleting a property."""
    response = client.delete(f"/api/properties/{init_database.id}")
    assert response.status_code == 200
    assert response.json["message"] == "Property deleted successfully"

    # Verify deletion
    get_response = client.get(f"/api/properties/{init_database.id}")
    assert get_response.status_code == 404


def test_filter_properties(client, init_database):
    """Test property filtering."""
    response = client.get("/api/properties?min_price=300000")
    assert response.status_code == 200
    assert len(response.json) > 0
    assert all(p["price"] >= 300000 for p in response.json)


def test_get_user_properties(client, init_database):
    """Test getting properties for a specific user."""
    response = client.get(f"/api/properties/user/{init_database.user_id}")
    assert response.status_code == 200
    assert len(response.json) > 0
    assert all(p["owner_id"] == init_database.user_id for p in response.json)
