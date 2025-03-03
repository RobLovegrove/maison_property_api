import pytest
from app.models import Property, Address, PropertySpecs  # Add this import


@pytest.fixture
def test_property_data(test_user):
    """Valid property data for tests."""
    return {
        "price": 350000,
        "seller_id": str(test_user.id),  # Changed from user_id to seller_id
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
        "status": "for_sale",  # Added status
    }


@pytest.fixture
def test_property(session, test_user):
    """Create a test property."""
    property = Property(
        price=350000,
        seller_id=test_user.id,  # Using string ID
        status="for_sale",
    )
    session.add(property)
    session.commit()  # Commit first to get the property.id

    # Add required address
    address = Address(
        property_id=property.id,  # Now property.id exists
        house_number="123",
        street="Test Street",
        city="London",
        postcode="SW1 1AA",
    )
    session.add(address)

    # Add required specs
    specs = PropertySpecs(
        property_id=property.id,  # Now property.id exists
        bedrooms=3,
        bathrooms=2,
        reception_rooms=1,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
    )
    session.add(specs)

    session.commit()  # Commit address and specs
    return property


def test_get_properties_empty(client, session):
    """Test GET /api/properties returns empty list when no properties exist"""
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert response.json == []


def test_create_property(client, test_property_data):
    """Test creating a property."""
    response = client.post(
        "/api/properties",
        json=test_property_data,
        headers={
            "Content-Type": "application/json"
        },  # Added content type header
    )
    assert response.status_code == 201
    assert "property_id" in response.json  # Changed from 'id'
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
        price=350000,
        seller_id=test_user.id,  # Changed from user_id
        status="for_sale",
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


def test_update_property(client, test_user, session):
    """Test updating a property."""
    # Create test property with all required fields
    property = Property(
        price=350000,
        seller_id=test_user.id,  # Changed from user_id
        status="for_sale",
        bedrooms=3,
        bathrooms=2,
    )
    session.add(property)
    session.commit()

    # Add required related objects
    address = Address(
        property_id=property.id,
        house_number="123",
        street="Test Street",
        city="London",
        postcode="SW1 1AA",
    )
    specs = PropertySpecs(
        property_id=property.id,
        bedrooms=3,
        bathrooms=2,
        reception_rooms=1,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
    )
    session.add_all([address, specs])
    session.commit()

    update_data = {
        "price": 375000,
        "status": "under_offer",
        "specs": {
            "bedrooms": 4,
            "bathrooms": 2,
            "reception_rooms": 2,
            "square_footage": 1500.0,
            "property_type": "semi-detached",
            "epc_rating": "A",
        },
    }

    response = client.put(
        f"/api/properties/{property.id}",
        json=update_data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


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


def test_get_user_properties(client, test_user, test_property):
    """Test getting properties for a specific user."""
    # Verify the property is associated with the test user
    assert test_property.seller_id == test_user.id

    response = client.get(f"/api/properties/user/{test_user.id}")
    assert response.status_code == 200

    properties = response.json
    assert len(properties) > 0
    assert str(properties[0]["seller_id"]) == test_user.id
