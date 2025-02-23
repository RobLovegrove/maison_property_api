from app import create_app, db
from app.models import User, Property, Address, PropertySpecs, PropertyMedia
from datetime import datetime, UTC
from uuid import uuid4
import random
from faker import Faker

fake = Faker()

def reset_database():
    """Reset and seed the database"""
    app = create_app('production')
    
    with app.app_context():
        # Log the database URL (masked)
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        masked_url = db_url.replace(db_url.split('@')[0].split(':')[2], '****')
        print(f"Connecting to database: {masked_url}")
        
        # Drop and recreate tables
        print("Dropping all tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        # Create test user
        user = User(
            email="test@maisonai.co.uk",
            name="Test User"
        )
        db.session.add(user)
        db.session.commit()

        # Define the standard image URL
        AZURE_IMAGE_URL = "https://maisonblobstorage.blob.core.windows.net/property-images/0dcb7f22-2216-42b5-adec-8ccbd3718474.jpg"

        # Create sample properties with explicit UUIDs
        for i in range(3):
            property_id = uuid4()
            print(f"Creating property with UUID: {property_id}")
            
            property = Property(
                id=property_id,
                price=350000 + (i * 50000),
                bedrooms=3,
                bathrooms=2,
                user_id=user.id,
                main_image_url=AZURE_IMAGE_URL,  # Set the main image URL
                created_at=datetime.now(UTC)
            )
            db.session.add(property)

            # Create media entry for the main image
            media = PropertyMedia(
                property_id=property_id,
                image_url=AZURE_IMAGE_URL,
                image_type="main",
                display_order=0
            )
            db.session.add(media)

            # Create address
            address = Address(
                property_id=property_id,
                house_number=str(123 + i),
                street="Sample Street",
                city="London",
                postcode="SW1 1AA"
            )
            db.session.add(address)

            # Create specs
            specs = PropertySpecs(
                property_id=property_id,
                bedrooms=3,
                bathrooms=2,
                reception_rooms=1,
                square_footage=1200.0,
                property_type="semi-detached",
                epc_rating="B"
            )
            db.session.add(specs)

        db.session.commit()
        print("Database reset complete!")

if __name__ == "__main__":
    reset_database() 