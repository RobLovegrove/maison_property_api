from app.main import app
from app.models import db, Property

# Sample data
SAMPLE_PROPERTIES = [
    Property(
        price=350000,
        address="123 Sample Street, London, SW1 1AA",
        bedrooms=3,
        bathrooms=2,
        reception_rooms=1,
        square_footage=1200.0,
        property_type="semi-detached",
        epc_rating="B",
        main_image_url="https://sample-images.com/property1.jpg"
    ),
    Property(
        price=250000,
        address="456 Test Road, Manchester, M1 2BB",
        bedrooms=2,
        bathrooms=1,
        reception_rooms=1,
        square_footage=800.0,
        property_type="apartment",
        epc_rating="C",
        main_image_url="https://sample-images.com/property2.jpg"
    )
]

def seed_database():
    with app.app_context():
        # Clear existing data
        Property.query.delete()
        
        # Add sample properties
        for property_item in SAMPLE_PROPERTIES:
            db.session.add(property_item)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database() 