import pytest
from app.main import app as flask_app
from app.models import db


@pytest.fixture
def app():
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/maison_test'
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def init_database():
    # Setup - create tables
    db.create_all()
    
    # Test runs here
    yield
    
    # Teardown - clear tables
    db.session.remove()
    db.drop_all()


@pytest.fixture
def sample_property():
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
