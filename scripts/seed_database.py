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
        main_image_url="https://sample-images.com/property1.jpg",
        description="""
        An exceptional three-bedroom semi-detached family home offering bright and spacious 
        accommodation throughout. Recently renovated to an excellent standard while maintaining 
        its period features, this property comprises a welcoming entrance hall, large reception 
        room with bay window, modern fitted kitchen with integrated appliances, and a stunning 
        conservatory overlooking the landscaped garden.

        The first floor offers three well-proportioned bedrooms and a contemporary family 
        bathroom. Additional benefits include off-street parking, a private rear garden, 
        and excellent transport links nearby.
        """.strip(),
        ownership_type="freehold",
        key_features=[
            "Recently renovated kitchen and bathroom",
            "Original Victorian features",
            "South-facing garden",
            "Off-street parking",
            "Close to outstanding schools",
            "Excellent transport links",
            "Bay windows with period features",
            "Modern integrated appliances"
        ],
        council_tax_band="D",
        additional_image_urls=[
            "https://sample-images.com/property1-kitchen.jpg",
            "https://sample-images.com/property1-living.jpg",
            "https://sample-images.com/property1-garden.jpg",
            "https://sample-images.com/property1-bathroom.jpg",
            "https://sample-images.com/property1-bedroom1.jpg"
        ],
        floorplan_url="https://sample-images.com/property1-floorplan.jpg",
        leasehold_years_remaining=None,
        property_age="Built circa 1890"
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
        main_image_url="https://sample-images.com/property2.jpg",
        description="""
        A stylish two-bedroom apartment in a prime Manchester location. This modern property 
        features an open-plan living space with floor-to-ceiling windows offering fantastic 
        city views. The contemporary kitchen comes fully equipped with high-end appliances.

        Both bedrooms are doubles, with the master bedroom benefiting from an en-suite 
        shower room. The property includes secure underground parking and a 24-hour concierge service.
        """.strip(),
        ownership_type="leasehold",
        key_features=[
            "Floor-to-ceiling windows",
            "City views",
            "Modern open-plan living",
            "Underground parking",
            "24-hour concierge",
            "En-suite to master bedroom",
            "High-end appliances",
            "Secure entry system"
        ],
        council_tax_band="C",
        additional_image_urls=[
            "https://sample-images.com/property2-kitchen.jpg",
            "https://sample-images.com/property2-living.jpg",
            "https://sample-images.com/property2-bedroom.jpg"
        ],
        floorplan_url="https://sample-images.com/property2-floorplan.jpg",
        leasehold_years_remaining=120,
        property_age="Built in 2015"
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