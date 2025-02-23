import pytest
from app import create_app, db
from uuid import UUID
from datetime import datetime
from app.models import User
import json
from io import BytesIO
from unittest.mock import patch
from werkzeug.datastructures import MultiDict


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


@pytest.fixture(scope="function")
def test_user(session):
    """Create a test user."""
    user = User(
        email=f"test_{datetime.now().timestamp()}@example.com",
        name="Test User",
    )
    session.add(user)
    session.commit()
    return session.get(User, user.id)  # Get fresh instance from session


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def create_test_property(client, test_user, session):
    """Helper function to create a test property"""
    data = {
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

    # Create a test image file
    test_image = BytesIO(b"fake image data")

    # Create the multipart form data
    form_data = MultiDict(
        [
            ("data", json.dumps(data)),
            ("main_image", (test_image, "test.jpg", "image/jpeg")),
        ]
    )

    response = client.post(
        "/api/properties", data=form_data, content_type="multipart/form-data"
    )

    assert response.status_code == 201
    return response.json["id"]


def test_create_property(client, test_user, session):
    """Test property creation"""
    property_id = create_test_property(client, test_user, session)
    assert UUID(property_id)


def test_get_property(client, test_user, session):
    """Test getting a single property"""
    # First create a property
    property_id = create_test_property(client, test_user, session)

    # Then retrieve it
    response = client.get(f"/api/properties/{property_id}")
    assert response.status_code == 200
    data = response.json
    assert data["price"] == 350000
    assert data["address"]["street"] == "Test Street"
    assert data["specs"]["bedrooms"] == 3
    assert (
        "main_image_url" in data
    )  # Just check it exists, don't check exact URL


def test_update_property(client, test_user, session):
    """Test property update"""
    # First create a property
    property_id = create_test_property(client, test_user, session)

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


def test_delete_property(client, test_user, session):
    """Test property deletion"""
    # Mock the blob storage service for testing
    with patch("app.blob_storage.BlobStorageService.delete_image"):
        # First create a property
        property_id = create_test_property(client, test_user, session)

        # Delete the property
        response = client.delete(f"/api/properties/{property_id}")
        assert response.status_code == 200


def test_get_properties_list(client, test_user, session):
    """Test getting list of properties with filters"""
    # Create a few properties
    create_test_property(client, test_user, session)
    create_test_property(client, test_user, session)

    response = client.get("/api/properties")
    assert response.status_code == 200
    assert len(response.json) >= 2
