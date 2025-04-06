import pytest  # noqa: F401
from app.models import UserRole


def test_create_user(client):
    """Test creating a new user"""
    data = {
        "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",  # Add Firebase UUID
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "+44123456789",
        "roles": [{"role_type": "buyer"}, {"role_type": "seller"}],
    }

    response = client.post(
        "/api/users", json=data, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 201
    assert response.json["user"]["first_name"] == "Test"
    assert response.json["user"]["last_name"] == "User"
    assert response.json["user"]["email"] == "test@example.com"
    assert len(response.json["user"]["roles"]) == 2


def test_create_user_duplicate_email(client):
    """Test creating a user with an existing email"""
    # First create a user
    data = {
        "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e6",  # Valid UUID
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "+44123456789",
    }

    client.post(
        "/api/users",
        json=data,
        headers={"Content-Type": "application/json"},  # Added headers
    )

    # Try to create another user with the same email
    data = {
        "user_id": "ce81f105-6945-56c0-b7f1-9842f62ff0f7",  # Valid UUID
        "first_name": "Another",
        "last_name": "User",
        "email": "test@example.com",  # Same email
        "phone_number": "+44987654321",
    }

    response = client.post(
        "/api/users", json=data, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert (
        response.json["error"] == "Email already registered"
    )  # Match exact error message


def test_create_user_missing_uuid(client):
    """Test creating a user without providing a UUID"""
    data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "+44123456789",
    }

    response = client.post(
        "/api/users", json=data, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    assert (
        response.json["error"]["user_id"][0]
        == "Missing data for required field."
    )  # Match Marshmallow's error format


def test_update_user(client, test_user):
    """Test updating a user's details."""
    response = client.put(
        f"/api/users/{test_user.id}",  # test_user.id is now a string
        json={
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.com",
        },
    )
    assert response.status_code == 200


def test_get_user_not_found(client):
    """Test getting a non-existent user"""
    response = client.get("/api/users/nonexistent-uuid")
    assert response.status_code == 404


def test_get_user_dashboard_empty(client):
    """Test getting dashboard for new user with no activity"""
    # Create a new user first
    user_data = {
        "user_id": "fd80f994-5834-45b9-a6f0-8731e51ff0e7",
        "first_name": "Dashboard",
        "last_name": "User",
        "email": "dashboard@test.com",
        "roles": [{"role_type": "buyer"}, {"role_type": "seller"}],
    }

    client.post(
        "/api/users",
        json=user_data,
        headers={"Content-Type": "application/json"},
    )

    # Get their dashboard
    response = client.get(f"/api/users/{user_data['user_id']}/dashboard")
    assert response.status_code == 200
    assert response.json["user"]["email"] == "dashboard@test.com"
    assert len(response.json["roles"]) == 2
    assert len(response.json["saved_properties"]) == 0
    assert len(response.json["listed_properties"]) == 0
    assert len(response.json["negotiations_as_buyer"]) == 0
    assert len(response.json["negotiations_as_seller"]) == 0


def test_get_users_list(client):
    """Test getting list of all users with role counts"""
    # Create a buyer
    buyer_data = {
        "user_id": "bd70f994-5834-45b9-a6f0-8731e51ff0e8",
        "first_name": "Buyer",
        "last_name": "User",
        "email": "buyer@test.com",
        "roles": [{"role_type": "buyer"}],
    }
    client.post(
        "/api/users",
        json=buyer_data,
        headers={"Content-Type": "application/json"},
    )

    # Create a seller
    seller_data = {
        "user_id": "cd80f994-5834-45b9-a6f0-8731e51ff0e9",
        "first_name": "Seller",
        "last_name": "User",
        "email": "seller@test.com",
        "roles": [{"role_type": "seller"}],
    }
    client.post(
        "/api/users",
        json=seller_data,
        headers={"Content-Type": "application/json"},
    )

    # Get users list
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.json["counts"]["total_buyers"] >= 1
    assert response.json["counts"]["total_sellers"] >= 1
    assert response.json["counts"]["total_unique_users"] >= 2
    assert len(response.json["buyers"]) >= 1
    assert len(response.json["sellers"]) >= 1


def test_update_user_not_found(client):
    """Test updating a non-existent user"""
    response = client.put(
        "/api/users/nonexistent-uuid",
        json={"first_name": "Updated"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 404


def test_update_user_invalid_email_format(client, test_user):
    """Test updating a user with invalid email format"""
    response = client.put(
        f"/api/users/{test_user.id}",
        json={"email": "invalid-email"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert "Not a valid email address" in str(response.json["error"])


def test_update_user_partial_fields(client, test_user):
    """Test updating only some fields of a user"""
    original_first_name = test_user.first_name
    response = client.put(
        f"/api/users/{test_user.id}",
        json={"phone_number": "07700900002"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.json["user"]["phone_number"] == "07700900002"
    # Verify other fields remain unchanged
    assert response.json["user"]["first_name"] == original_first_name


def test_user_dashboard_with_activity(
    client, test_user, test_property, test_seller, session
):
    """Test dashboard with saved properties and negotiations"""
    # Set up buyer role for test_user
    buyer_role = UserRole(user_id=test_user.id, role_type="buyer")
    session.add(buyer_role)
    session.commit()

    # Save a property
    save_response = client.post(
        f"/api/users/{test_user.id}/saved-properties",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "notes": "Test note",
        },
        headers={"Content-Type": "application/json"},
    )
    assert save_response.status_code == 201

    # Make an offer
    offer_response = client.post(
        f"/api/users/{test_user.id}/offers",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "offer_amount": 300000,
        },
        headers={"Content-Type": "application/json"},
    )
    assert offer_response.status_code == 201

    # Get dashboard and verify activity
    response = client.get(f"/api/users/{test_user.id}/dashboard")
    assert response.status_code == 200
    assert len(response.json["saved_properties"]) > 0
    assert len(response.json["negotiations_as_buyer"]) > 0

    # Verify saved property details
    saved_property = response.json["saved_properties"][0]
    assert saved_property["property_id"] == str(
        test_property.id
    )  # Convert UUID to string for comparison
    assert saved_property["notes"] == "Test note"

    # Verify negotiation details
    negotiation = response.json["negotiations_as_buyer"][0]
    assert negotiation["property_id"] == str(
        test_property.id
    )  # Convert UUID to string for comparison
    assert negotiation["status"] == "active"
    assert len(negotiation["transaction_history"]) > 0
    assert negotiation["transaction_history"][0]["offer_amount"] == 300000
