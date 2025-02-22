import pytest
from app import create_app, db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    User,
)
from datetime import datetime, UTC


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    app = create_app("testing")
    app.config.update(
        {"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
    )
    return app


@pytest.fixture(scope="session")
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test runner for CLI commands."""
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
    return session.get(User, user.id)


@pytest.fixture(scope="function")
def init_database(app, session, test_user):
    """Initialize test database with sample data."""
    # Create test property with all related data
    property = Property(
        price=350000,
        bedrooms=3,
        bathrooms=2.0,
        user_id=test_user.id,
        created_at=datetime.now(UTC),
        last_updated=datetime.now(UTC),
    )

    session.add(property)
    session.flush()  # Get ID before creating related objects

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
    return session.get(Property, property.id)  # Get fresh instance


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


@pytest.fixture
def sample_property(test_user):
    """Sample property data for tests."""
    return {
        "price": 350000,
        "user_id": test_user.id,
        "bedrooms": 3,
        "bathrooms": 2,
        "main_image_url": "https://example.com/main.jpg",
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
