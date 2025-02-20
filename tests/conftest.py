import pytest
from app import create_app, db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    PropertyFeatures,
    PropertyDetail,
    PropertyMedia,
)
from datetime import datetime, UTC
from sqlalchemy import text


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    app = create_app("testing")

    # Create tables for test database
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


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
def init_database(app):
    """Initialize test database with sample data."""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        try:
            # Clear all tables
            db.session.execute(text("TRUNCATE TABLE property_media CASCADE"))
            db.session.execute(
                text("TRUNCATE TABLE property_features CASCADE")
            )
            db.session.execute(text("TRUNCATE TABLE property_specs CASCADE"))
            db.session.execute(text("TRUNCATE TABLE property_details CASCADE"))
            db.session.execute(text("TRUNCATE TABLE addresses CASCADE"))
            db.session.execute(text("TRUNCATE TABLE properties CASCADE"))
            db.session.commit()
        except Exception as e:
            print(f"Warning: Could not truncate tables: {e}")
            db.session.rollback()

        # Create test property with all related data
        property = Property(
            price=350000,
            bedrooms=3,
            bathrooms=2.0,
            main_image_url="https://example.com/main.jpg",
            created_at=datetime.now(UTC),
            last_updated=datetime.now(UTC),
        )

        # Create address
        address = Address(
            property=property,
            house_number="123",
            street="Test Street",
            city="London",
            postcode="SW1 1AA",
            latitude=51.5074,
            longitude=-0.1278,
        )

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

        # Create features
        features = PropertyFeatures(
            property=property,
            has_garden=True,
            garden_size=100.0,
            parking_spaces=2,
            has_garage=True,
        )

        # Create details
        details = PropertyDetail(
            property=property,
            description="A lovely property",
            property_type="semi-detached",
            construction_year=1990,
            parking_spaces=2,
            heating_type="Gas Central",
        )

        # Create media entries
        main_image = PropertyMedia(
            property=property,
            image_url="https://example.com/main.jpg",
            image_type="main",
            display_order=0,
        )

        additional_image = PropertyMedia(
            property=property,
            image_url="https://example.com/additional1.jpg",
            image_type="additional",
            display_order=1,
        )

        floorplan = PropertyMedia(
            property=property,
            image_url="https://example.com/floorplan.pdf",
            image_type="floorplan",
            display_order=None,
        )

        # Add all objects to session
        db.session.add(property)
        db.session.add(address)
        db.session.add(specs)
        db.session.add(features)
        db.session.add(details)
        db.session.add(main_image)
        db.session.add(additional_image)
        db.session.add(floorplan)
        db.session.commit()

        yield db

        # Clean up
        db.session.rollback()


@pytest.fixture(scope="function")
def session(app):
    """Create a new database session for a test."""
    with app.app_context():
        # Start transaction
        db.session.begin_nested()

        # Create fresh tables
        db.drop_all()
        db.create_all()

        yield db.session

        # Rollback transaction
        db.session.rollback()
        db.session.remove()


@pytest.fixture
def sample_property():
    """Sample property data for tests."""
    return {
        "price": 350000,
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
