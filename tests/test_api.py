import pytest
from app import create_app, db


@pytest.fixture
def app():
    app = create_app("testing")

    # Create all tables
    with app.app_context():
        db.create_all()

    yield app

    # Clean up after test
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def create_test_property(client):
    """Helper function to create a test property and return its ID"""
    test_property = {
        "price": 350000,
        "address": {
            "house_number": "42",
            "street": "Test Street",
            "city": "Test City",
            "postcode": "TE1 1ST",
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "reception_rooms": 1,
            "square_footage": 1200.0,
            "property_type": "semi-detached",
            "epc_rating": "B",
        },
        "details": {
            "description": "A lovely test property",
            "property_type": "semi-detached",
            "construction_year": 2020,
            "parking_spaces": 2,
            "heating_type": "gas",
        },
    }

    response = client.post("/api/properties", json=test_property)
    assert response.status_code == 201
    assert "id" in response.json
    return response.json["id"]


def test_create_property(client):
    """Test property creation"""
    property_id = create_test_property(client)
    assert property_id is not None


def test_get_property(client, init_database):
    """Test getting a single property"""
    # First create a property
    property_id = create_test_property(client)

    # Then retrieve it
    response = client.get(f"/api/properties/{property_id}")
    assert response.status_code == 200
    data = response.json
    assert data["price"] == 350000
    assert data["address"]["street"] == "Test Street"
    assert data["specs"]["bedrooms"] == 3


def test_update_property(client, init_database):
    """Test property update"""
    # First create a property
    property_id = create_test_property(client)

    update_data = {
        "price": 375000,
        "specs": {
            "bedrooms": 4,
            "bathrooms": 2,
            "reception_rooms": 2,
            "square_footage": 1500.0,
            "property_type": "semi-detached",
            "epc_rating": "A",
        },
    }

    response = client.put(f"/api/properties/{property_id}", json=update_data)
    assert response.status_code == 200

    # Verify the update
    get_response = client.get(f"/api/properties/{property_id}")
    assert get_response.status_code == 200
    updated_data = get_response.json
    assert updated_data["price"] == 375000
    assert updated_data["specs"]["bedrooms"] == 4


def test_delete_property(client, init_database):
    """Test property deletion"""
    # First create a property
    property_id = create_test_property(client)

    # Delete the property
    response = client.delete(f"/api/properties/{property_id}")
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(f"/api/properties/{property_id}")
    assert get_response.status_code == 404


def test_get_properties_list(client, init_database):
    """Test getting list of properties with filters"""
    # Create a few properties
    create_test_property(client)
    create_test_property(client)

    # Remove trailing slash from URLs
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert len(response.json) >= 2

    # Test with filters
    response = client.get("/api/properties?min_price=300000")
    assert response.status_code == 200
    for property in response.json:
        assert property["price"] >= 300000
