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
