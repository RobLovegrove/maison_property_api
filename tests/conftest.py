import pytest
from app import create_app, db


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:postgres@localhost:5432/maison_test"
    )
    return _app


@pytest.fixture(scope="function")
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def app_context(app):
    """Create fresh database tables."""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def session(app_context, app):
    """Database session for tests."""
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_property():
    """Sample property data for tests."""
    property_data = {
        "price": 350000,
        "address": "123 Test Street, London, SW1 1AA",
        "bedrooms": 3,
        "bathrooms": 2,
        "reception_rooms": 1,
        "square_footage": 1200.0,
        "property_type": "semi-detached",
        "epc_rating": "B",
        "main_image_url": "https://test-images.com/property1.jpg",
        "description": "A test property description",
        "ownership_type": "freehold",
        "key_features": ["Feature 1", "Feature 2"],
        "council_tax_band": "D",
    }
    return property_data
