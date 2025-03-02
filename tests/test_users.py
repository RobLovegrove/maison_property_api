def test_create_user(client):
    """Test user creation."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+44123456789",
    }

    response = client.post("/api/users", json=data)
    assert response.status_code == 201
    assert "user" in response.json
    assert response.json["user"]["email"] == data["email"]
    assert response.json["user"]["full_name"] == "John Doe"


def test_create_user_duplicate_email(client, test_user):
    """Test creating user with duplicate email."""
    data = {"first_name": "Jane", "last_name": "Doe", "email": test_user.email}

    response = client.post("/api/users", json=data)
    assert response.status_code == 400
    assert "error" in response.json
    assert "already registered" in response.json["error"]


def test_update_user(client, test_user):
    """Test updating user details."""
    data = {"first_name": "Jane", "phone_number": "+44987654321"}

    response = client.put(f"/api/users/{test_user.id}", json=data)
    assert response.status_code == 200
    assert response.json["user"]["first_name"] == "Jane"
    assert response.json["user"]["phone_number"] == "+44987654321"
