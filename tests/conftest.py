import pytest
from app.main import app as flask_app
from app.models import db, Property

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///property_db_test'
    
    with flask_app.app_context():
        # Drop and recreate all tables before each test
        db.drop_all()
        db.create_all()
        yield flask_app
        # Clean up after test
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

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
        "council_tax_band": "D"
    }
    return property_data 