import pytest
from app import create_app, db
from uuid import UUID
from app.models import User, UserRole
from datetime import datetime


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
    """Create a test user with buyer and seller roles."""
    user = User(
        id="test-user-id",
        first_name="Test",
        last_name="User",
        email=f"test_{datetime.now().timestamp()}@example.com",
        phone_number="+44123456789",
    )
    session.add(user)

    # Add both buyer and seller roles
    roles = [
        UserRole(user_id=user.id, role_type="buyer"),
        UserRole(user_id=user.id, role_type="seller"),
    ]
    session.add_all(roles)
    session.commit()
    return user


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def create_test_property(client, test_user, session):
    """Helper function to create a test property"""
    data = {
        "price": 350000,
        "seller_id": str(test_user.id),
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
        "status": "for_sale",
    }

    response = client.post(
        "/api/properties",
        json=data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 201
    return response.json["property_id"]


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
        f"/api/properties/{property_id}",
        json=update_data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200


def test_delete_property(client, test_user, session):
    """Test property deletion"""
    # First create a property
    property_id = create_test_property(client, test_user, session)

    # Delete the property
    response = client.delete(f"/api/properties/{property_id}")
    assert response.status_code == 200

    # Verify deletion
    get_response = client.get(f"/api/properties/{property_id}")
    assert get_response.status_code == 404


def test_get_properties_list(client, test_user, session):
    """Test getting list of properties with filters"""
    # Create a few properties
    create_test_property(client, test_user, session)
    create_test_property(client, test_user, session)

    response = client.get("/api/properties")
    assert response.status_code == 200
    assert len(response.json) >= 2


def test_get_user_dashboard(client, test_user, session):
    """Test getting a user's dashboard data after login"""
    # First create some test properties owned by the user
    property_id = create_test_property(client, test_user, session)

    # Get the dashboard data
    response = client.get(f"/api/users/{test_user.id}/dashboard")
    assert response.status_code == 200

    data = response.json
    # Check basic user info
    assert data["user"]["first_name"] == "Test"
    assert data["user"]["last_name"] == "User"
    assert data["user"]["email"]

    # Check roles
    assert len(data["roles"]) == 2
    role_types = [role["role_type"] for role in data["roles"]]
    assert "buyer" in role_types
    assert "seller" in role_types

    # Check properties (as seller)
    assert len(data["listed_properties"]) == 1
    listed_property = data["listed_properties"][0]
    assert listed_property["property_id"] == property_id
    assert "status" in listed_property
    assert listed_property["status"] == "for_sale"

    # Check saved properties and negotiations
    assert "saved_properties" in data
    assert "negotiations_as_buyer" in data
