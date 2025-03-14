import pytest
from app import create_app, db
from app.models import (
    Property,
    User,
    PropertyMedia,
)
from datetime import datetime, UTC
from unittest.mock import patch
from app.blob_storage import MockBlobStorageService
from uuid import uuid4


@pytest.fixture(scope="function")
def app():
    """Create application for the tests."""
    app = create_app("testing")

    with app.app_context():
        # Create tables
        db.create_all()
        yield app
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def session(app):
    """Create a new database session for a test."""
    with app.app_context():
        # Create tables
        db.create_all()

        # Get session
        session = db.session

        yield session

        # Clean up
        session.close()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def app_context(app):
    """Create an application context."""
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def test_user(session):
    """Create a test user."""
    user = User(
        id="test-user-id",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        phone_number="+1234567890",
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture(scope="function")
def test_seller(session):
    """Create a test seller."""
    seller = User(
        id="seller-id",
        email="seller@example.com",
        first_name="Test",
        last_name="Seller",
        phone_number="+1234567891",
    )
    session.add(seller)
    session.commit()
    return seller


@pytest.fixture(scope="function")
def init_database(app, session, test_user):
    """Initialize test database with sample data."""
    # Create test property with all related data and consolidated fields
    property = Property(
        id=uuid4(),  # Add explicit UUID
        price=350000,
        bedrooms=3,
        bathrooms=2.0,
        seller_id=test_user.id,
        main_image_url=(
            "https://maisonblobstorage.blob.core.windows.net/"
            "property-images/"
            "0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
        ),
        created_at=datetime.now(UTC),
        last_updated=datetime.now(UTC),
        # Address fields
        house_number="123",
        street="Test Street",
        city="London",
        postcode="SW1 1AA",
        latitude=51.5074,
        longitude=-0.1278,
        # Specs fields
        reception_rooms=2,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
    )

    session.add(property)
    session.flush()  # Get ID before creating related objects

    # Create media
    media = [
        PropertyMedia(
            property=property,
            image_url=(
                "https://maisonblobstorage.blob.core.windows.net/"
                "property-images/"
                "0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
            ),
            image_type="main",
            display_order=1,
        ),
        PropertyMedia(
            property=property,
            image_url=(
                "https://maisonblobstorage.blob.core.windows.net/"
                "property-images/"
                "0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
            ),
            image_type="interior",
            display_order=2,
        ),
        PropertyMedia(
            property=property,
            image_url="https://example.com/floorplan.pdf",
            image_type="floorplan",
            display_order=3,
        ),
    ]
    session.add_all(media)
    session.commit()
    return property


@pytest.fixture
def test_property_data(test_user):
    """Valid property data for tests."""
    return {
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


@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    """Mock all external services for tests"""
    # Create an instance of MockBlobStorageService
    mock_service = MockBlobStorageService()

    # Replace the BlobStorageService class with our mock instance
    monkeypatch.setattr(
        "app.properties.BlobStorageService",
        lambda: mock_service,
    )

    with patch("app.utils.geocode_address") as mock_geocode:
        mock_geocode.return_value = (51.5074, -0.1278)  # London coordinates
        yield mock_geocode


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set required environment variables for testing"""
    monkeypatch.setenv(
        "AZURE_STORAGE_CONNECTION_STRING", "mock_connection_string"
    )
    monkeypatch.setenv("FLASK_ENV", "testing")


@pytest.fixture(scope="function")
def test_property(session, test_seller):
    """Create a test property with consolidated fields."""
    property = Property(
        price=350000,
        seller_id=test_seller.id,
        status="for_sale",
        # Address fields
        house_number="123",
        street="Test Street",
        city="London",
        postcode="SW1 1AA",
        latitude=51.5074,
        longitude=-0.1278,
        # Specs fields
        bedrooms=3,
        bathrooms=2,
        reception_rooms=1,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
    )
    session.add(property)
    session.commit()
    return property
