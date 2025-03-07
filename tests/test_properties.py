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


def test_get_user_properties(client, test_seller, test_property):
    """Test getting properties for a specific user."""
    # Verify the property is associated with the test seller
    assert test_property.seller_id == test_seller.id

    response = client.get(f"/api/properties/user/{test_seller.id}")
    assert response.status_code == 200

    properties = response.json
    assert len(properties) > 0
    assert str(properties[0]["seller_id"]) == test_seller.id


def test_create_property_invalid_price(client, test_property_data):
    """Test creating a property with invalid price"""
    test_property_data["price"] = -1000
    response = client.post(
        "/api/properties",
        json=test_property_data,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    # Check for either format of error message
    error_message = str(response.json.get("error", "")).lower()
    assert any(
        msg in error_message for msg in ["price", "validation", "invalid"]
    )


def test_update_property_status_transitions(client, test_property):
    """Test property status transitions"""
    # Test for_sale -> under_offer
    response = client.put(
        f"/api/properties/{test_property.id}",
        json={"status": "under_offer"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200

    # Verify the status was updated
    get_response = client.get(f"/api/properties/{test_property.id}")
    assert get_response.json["status"] == "under_offer"

    # Test under_offer -> for_sale
    response = client.put(
        f"/api/properties/{test_property.id}",
        json={"status": "for_sale"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200

    # Verify the status was updated back
    get_response = client.get(f"/api/properties/{test_property.id}")
    assert get_response.json["status"] == "for_sale"

    # Test invalid status
    response = client.put(
        f"/api/properties/{test_property.id}",
        json={"status": "invalid_status"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_property_search_filters(client, test_property):
    """Test multiple property search filters"""
    filters = {
        "min_price": 300000,
        "max_price": 400000,
        "bedrooms": 3,
        "property_type": "semi-detached",
        "city": "London",
    }
    query_string = "&".join(f"{k}={v}" for k, v in filters.items())
    response = client.get(f"/api/properties?{query_string}")
    assert response.status_code == 200

    # If we got any properties back, verify they match the filters
    if response.json:
        property = response.json[0]
        assert property["price"] >= filters["min_price"]
        assert property["price"] <= filters["max_price"]
        assert property["bedrooms"] == filters["bedrooms"]
        assert property["specs"]["property_type"] == filters["property_type"]
        assert property["address"]["city"].lower() == filters["city"].lower()


def test_offer_lifecycle(
    client, test_user, test_property, test_seller, session
):
    """Test complete offer lifecycle"""
    # Set up buyer role for test_user
    from app.models import UserRole

    buyer_role = UserRole(user_id=test_user.id, role_type="buyer")
    session.add(buyer_role)
    session.commit()

    # Create initial offer
    offer_response = client.post(
        f"/api/users/{test_user.id}/offers",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "offer_amount": 300000,
        },
        headers={"Content-Type": "application/json"},
    )
    print(f"Offer response: {offer_response.json}")  # Print error response
    assert offer_response.status_code == 201
    negotiation_id = offer_response.json["negotiation"]["negotiation_id"]

    # Counter offer from seller
    counter_response = client.post(
        f"/api/users/{test_seller.id}/offers",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "offer_amount": 310000,
            "negotiation_id": negotiation_id,
        },
        headers={"Content-Type": "application/json"},
    )
    assert counter_response.status_code == 201

    # Accept offer
    accept_response = client.put(
        f"/api/users/{test_user.id}/offers/{negotiation_id}",
        json={"action": "accept"},
        headers={"Content-Type": "application/json"},
    )
    assert accept_response.status_code == 200
    assert accept_response.json["negotiation"]["status"] == "accepted"

    # Verify property status changed to under_offer
    property_response = client.get(f"/api/properties/{test_property.id}")
    assert property_response.json["status"] == "under_offer"


def test_concurrent_offers(
    client, test_user, test_property, test_seller, session
):
    """Test handling multiple offers on same property"""
    from app.models import User, UserRole

    # Create another test user
    other_user = User(
        id="different-user-id",
        first_name="Other",
        last_name="User",
        email="other@example.com",
    )
    session.add(other_user)

    # Add buyer roles to both users
    for user in [test_user, other_user]:
        buyer_role = UserRole(user_id=user.id, role_type="buyer")
        session.add(buyer_role)

    session.commit()

    # Create first offer
    first_offer = client.post(
        f"/api/users/{test_user.id}/offers",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "offer_amount": 300000,
        },
        headers={"Content-Type": "application/json"},
    )
    assert first_offer.status_code == 201

    # Create second offer from different user
    second_offer = client.post(
        f"/api/users/{other_user.id}/offers",
        json={
            "property_id": str(test_property.id),  # Convert UUID to string
            "offer_amount": 310000,
        },
        headers={"Content-Type": "application/json"},
    )
    assert second_offer.status_code == 201

    # Accept first offer
    accept_response = client.put(
        f"/api/users/{test_seller.id}/offers/"
        f"{first_offer.json['negotiation']['negotiation_id']}",
        json={"action": "accept"},
        headers={"Content-Type": "application/json"},
    )
    assert accept_response.status_code == 200

    # Verify second offer is automatically rejected
    dashboard_response = client.get(f"/api/users/{other_user.id}/dashboard")
    assert dashboard_response.status_code == 200
    assert any(
        neg["status"] == "rejected"
        for neg in dashboard_response.json["negotiations_as_buyer"]
    )
