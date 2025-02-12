import json


def test_get_properties_empty(client):
    """Test GET /api/properties returns empty list when no properties exist"""
    response = client.get("/api/properties")
    assert response.status_code == 200
    assert response.json == []


def test_create_property(client, sample_property):
    """Test POST /api/properties creates a new property"""
    response = client.post(
        "/api/properties",
        data=json.dumps(sample_property),
        content_type="application/json",
    )
    assert response.status_code == 201
    assert "id" in response.json

    # Verify property was created
    get_response = client.get(f'/api/properties/{response.json["id"]}')
    assert get_response.status_code == 200
    assert get_response.json["basic_info"]["address"] == sample_property["address"]


def test_get_property_detail(client, sample_property):
    """Test GET /api/properties/<id> returns detailed property information"""
    # Create property first
    create_response = client.post(
        "/api/properties",
        data=json.dumps(sample_property),
        content_type="application/json",
    )
    property_id = create_response.json["id"]

    # Get property details
    response = client.get(f"/api/properties/{property_id}")
    assert response.status_code == 200
    assert response.json["basic_info"]["address"] == sample_property["address"]
    assert response.json["description"] == sample_property["description"]
    assert response.json["key_features"] == sample_property["key_features"]


def test_update_property(client, sample_property):
    """Test PUT /api/properties/<id> updates property information"""
    # Create property first
    create_response = client.post(
        "/api/properties",
        data=json.dumps(sample_property),
        content_type="application/json",
    )
    property_id = create_response.json["id"]

    # Update property
    update_data = {"price": 375000, "description": "Updated description"}
    response = client.put(
        f"/api/properties/{property_id}",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Verify update
    get_response = client.get(f"/api/properties/{property_id}")
    assert get_response.json["basic_info"]["price"] == 375000
    assert get_response.json["description"] == "Updated description"


def test_delete_property(client, sample_property):
    """Test DELETE /api/properties/<id> removes the property"""
    # Create property first
    create_response = client.post(
        "/api/properties",
        data=json.dumps(sample_property),
        content_type="application/json",
    )
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
        "price": "not a number",  # Invalid type
        "address": 123,  # Invalid type
    }
    response = client.post(
        "/api/properties",
        data=json.dumps(invalid_property),
        content_type="application/json",
    )
    assert response.status_code == 400
    assert "errors" in response.json
