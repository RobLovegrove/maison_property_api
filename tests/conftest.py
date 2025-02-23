import pytest
from app import create_app, db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    User,
    PropertyMedia,
)
from datetime import datetime, UTC
from unittest.mock import patch
from app.blob_storage import MockBlobStorageService


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
        email=f"test_{datetime.now().timestamp()}@example.com",
        name="Test User",
        created_at=datetime.now(UTC),
    )
    session.add(user)
    session.commit()
    session.refresh(user)  # Ensure we have the latest data
    return user


@pytest.fixture(scope="function")
def init_database(app, session, test_user):
    """Initialize test database with sample data."""
    # Create test property with all related data
    property = Property(
        price=350000,
        bedrooms=3,
        bathrooms=2.0,
        user_id=test_user.id,
        main_image_url=(
            "https://maisonblobstorage.blob.core.windows.net/"
            "property-images/"
            "0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
        ),
        created_at=datetime.now(UTC),
        last_updated=datetime.now(UTC),
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

    # Create address
    address = Address(
        property=property,
        house_number="123",
        street="Test Street",
        city="London",
        postcode="SW1 1AA",
    )
    session.add(address)

    # Create specs
    specs = PropertySpecs(
        property=property,
        bedrooms=3,
        bathrooms=2,
        reception_rooms=2,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
    )
    session.add(specs)

    session.commit()
    return property


@pytest.fixture
def sample_property(test_user):
    """Sample property data for tests."""
    return {
        "price": 350000,
        "user_id": test_user.id,
        "bedrooms": 3,
        "bathrooms": 2,
        "main_image_url": (
            "https://maisonblobstorage.blob.core.windows.net/"
            "property-images/"
            "0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"
        ),
        "address": {
            "house_number": "123",
            "street": "Test Street",
            "city": "London",
            "postcode": "SW1 1AA",
        },
        "specs": {
            "bedrooms": 3,
            "bathrooms": 2,
            "reception_rooms": 1,
            "square_footage": 1200.0,
            "property_type": "semi-detached",
            "epc_rating": "B",
        },
        "features": {
            "has_garden": True,
            "garden_size": 100.0,
            "parking_spaces": 2,
            "has_garage": True,
        },
        "details": {
            "description": "A lovely property",
            "property_type": "semi-detached",
            "construction_year": 1990,
            "parking_spaces": 2,
            "heating_type": "Gas Central",
        },
    }


@pytest.fixture(autouse=True)
def mock_services(monkeypatch):
    """Mock all external services for tests"""
    # Create an instance of MockBlobStorageService
    mock_service = MockBlobStorageService()

    # Replace the BlobStorageService class with our mock instance
    monkeypatch.setattr(
        "app.properties.BlobStorageService",  # Change this line
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
