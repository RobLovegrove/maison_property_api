from app import create_app, db
from app.models import User, Property, Address, PropertySpecs, PropertyFeatures
from datetime import datetime, UTC
from uuid import uuid4

def reset_database():
    """Drop all tables and recreate them"""
    app = create_app('production')
    
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating new tables...")
        db.create_all()
        
        # Create test user
        print("Creating test user...")
        user = User(
            id=1,  # Set explicit ID for testing
            email="test@maisonai.co.uk",
            name="Test User",
            created_at=datetime.now(UTC)
        )
        db.session.add(user)
        db.session.commit()

        # Create sample properties
        print("Creating sample properties...")
        for i in range(3):  # Create 3 sample properties
            property = Property(
                id=uuid4(),
                price=350000 + (i * 50000),
                user_id=user.id,
                bedrooms=3,
                bathrooms=2,
                created_at=datetime.now(UTC),
                last_updated=datetime.now(UTC)
            )
            
            # Add required address
            address = Address(
                house_number=str(123 + i),
                street="Sample Street",
                city="London",
                postcode="SW1 1AA",
                property=property
            )
            
            # Add required specs
            specs = PropertySpecs(
                bedrooms=3,
                bathrooms=2,
                reception_rooms=1,
                square_footage=1200.0,
                property_type="semi-detached",
                epc_rating="B",
                property=property
            )
            
            db.session.add(property)
            db.session.add(address)
            db.session.add(specs)
            
        db.session.commit()
        
        print("Database reset complete!")

if __name__ == "__main__":
    reset_database() 