from app import create_app, db
from app.models import User, Property, Address, PropertySpecs, PropertyMedia, PropertyDetail, PropertyFeatures, UserRole, SavedProperty
from datetime import datetime, UTC
from uuid import uuid4
import random
from faker import Faker
import uuid

fake = Faker()

def create_user_with_roles(user_id, is_seller=True, is_buyer=False):
    """Helper function to create a user with specified roles"""
    user = User(
        id=user_id,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        phone_number=f"+44{fake.msisdn()[3:]}"  # Generate UK-style number
    )
    db.session.add(user)

    if is_seller:
        seller_role = UserRole(
            user_id=user_id,
            role_type='seller'
        )
        db.session.add(seller_role)
    
    if is_buyer:
        buyer_role = UserRole(
            user_id=user_id,
            role_type='buyer'
        )
        db.session.add(buyer_role)

    return user

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
        
        # Create specific user with fixed UUID and roles
        specific_user_id = uuid.UUID('3613c096-f41f-479f-a09f-7e0ab53b4eda')
        user = create_user_with_roles(specific_user_id, is_seller=True, is_buyer=True)

        # Create additional random seller for variety
        additional_seller_id = uuid4()
        additional_seller = create_user_with_roles(additional_seller_id, is_seller=True, is_buyer=False)

        # Define all image URLs that will be used for all properties
        property_images = [
            "https://maisonblobstorage.blob.core.windows.net/property-images/2ea1d64a-18da-4752-9b1e-fa40dccd8da9.jpg",
            "https://maisonblobstorage.blob.core.windows.net/property-images/1dcca3e5-8119-41e4-9349-a78a54546292.jpg",
            "https://maisonblobstorage.blob.core.windows.net/property-images/9b8ecccb-e837-4a64-9f87-8b743420c023.jpg",
            "https://maisonblobstorage.blob.core.windows.net/property-images/1ca9765e-bc94-4ab1-b677-c038f099d5a3.jpg",
            "https://maisonblobstorage.blob.core.windows.net/property-images/68fb996d-ce89-4d0e-a79a-0a0df1a7ce97.jpg"
        ]

        # Update additional_properties to alternate between sellers
        seller_ids = [specific_user_id, additional_seller_id]
        
        # Create specific property with fixed UUID
        specific_property_id = uuid.UUID('5ea12e39-bff9-48e2-b593-eb13b5908959')
        property = Property(
            id=specific_property_id,
            price=350000,
            bedrooms=3,
            bathrooms=2,
            seller_id=specific_user_id,  # Changed from user_id
            main_image_url=property_images[0],
            created_at=datetime.now(UTC),
            status='for_sale'
        )
        db.session.add(property)

        # Add all images to the specific property
        for i, image_url in enumerate(property_images):
            media = PropertyMedia(
                property_id=specific_property_id,
                image_url=image_url,
                image_type="image",
                display_order=i
            )
            db.session.add(media)

        # Create address for specific property
        address = Address(
            property_id=specific_property_id,
            house_number="123",
            street="Sample Street",
            city="London",
            postcode="SW1 1AA"
        )
        db.session.add(address)

        # Create specs for specific property
        specs = PropertySpecs(
            property_id=specific_property_id,
            bedrooms=3,
            bathrooms=2,
            reception_rooms=1,
            square_footage=1200.0,
            property_type="semi-detached",
            epc_rating="B"
        )
        db.session.add(specs)

        # Create details for specific property
        details = PropertyDetail(
            property_id=specific_property_id,
            description="A beautiful property...",
            construction_year=2020,
            heating_type="gas central"
        )
        db.session.add(details)

        # Create features for specific property
        features = PropertyFeatures(
            property_id=specific_property_id,
            has_garden=True,
            garden_size=100.0,
            parking_spaces=2,
            has_garage=True
        )
        db.session.add(features)

        # Create additional properties
        additional_properties = [
            {
                "price": 425000,
                "bedrooms": 4,
                "bathrooms": 2,
                "main_image_url": property_images[0],
                "status": "for_sale",
                "address": {
                    "house_number": "45",
                    "street": "Oak Avenue",
                    "city": "Manchester",
                    "postcode": "M20 3PS"
                },
                "specs": {
                    "bedrooms": 4,
                    "bathrooms": 2,
                    "reception_rooms": 2,
                    "square_footage": 1500.0,
                    "property_type": "detached",
                    "epc_rating": "B"
                },
                "features": {
                    "has_garden": True,
                    "garden_size": 200.0,
                    "parking_spaces": 2,
                    "has_garage": True
                }
            },
            {
                "price": 295000,
                "bedrooms": 2,
                "bathrooms": 1,
                "main_image_url": property_images[0],
                "status": "under_offer",
                "address": {
                    "house_number": "12B",
                    "street": "High Street",
                    "city": "Bristol",
                    "postcode": "BS1 4DP"
                },
                "specs": {
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "reception_rooms": 1,
                    "square_footage": 850.0,
                    "property_type": "apartment",
                    "epc_rating": "C"
                },
                "features": {
                    "has_garden": False,
                    "garden_size": None,
                    "parking_spaces": 1,
                    "has_garage": False
                }
            },
            {
                "price": 550000,
                "bedrooms": 5,
                "bathrooms": 3,
                "main_image_url": property_images[0],
                "status": "sold",
                "address": {
                    "house_number": "78",
                    "street": "Church Lane",
                    "city": "Edinburgh",
                    "postcode": "EH1 2BN"
                },
                "specs": {
                    "bedrooms": 5,
                    "bathrooms": 3,
                    "reception_rooms": 3,
                    "square_footage": 2200.0,
                    "property_type": "detached",
                    "epc_rating": "A"
                },
                "features": {
                    "has_garden": True,
                    "garden_size": 400.0,
                    "parking_spaces": 3,
                    "has_garage": True
                }
            }
        ]

        for idx, prop_data in enumerate(additional_properties):
            # Alternate between sellers
            seller_id = seller_ids[idx % len(seller_ids)]
            
            property = Property(
                id=uuid4(),
                price=prop_data["price"],
                bedrooms=prop_data["bedrooms"],
                bathrooms=prop_data["bathrooms"],
                seller_id=seller_id,  # Alternate between sellers
                main_image_url=property_images[0],
                created_at=datetime.now(UTC),
                status=prop_data["status"]
            )
            db.session.add(property)

            # Add all images to this property
            for i, image_url in enumerate(property_images):
                media = PropertyMedia(
                    property_id=property.id,
                    image_url=image_url,
                    image_type="image",
                    display_order=i
                )
                db.session.add(media)

            # Create address
            address = Address(
                property_id=property.id,
                **prop_data["address"]
            )
            db.session.add(address)

            # Create specs
            specs = PropertySpecs(
                property_id=property.id,
                **prop_data["specs"]
            )
            db.session.add(specs)

            # Create features
            features = PropertyFeatures(
                property_id=property.id,
                **prop_data["features"]
            )
            db.session.add(features)

            # Create details
            details = PropertyDetail(
                property_id=property.id,
                description=f"A beautiful {prop_data['specs']['property_type']} property in {prop_data['address']['city']}",
                construction_year=2020,
                heating_type="gas central"
            )
            db.session.add(details)

            # Add as saved property
            saved = SavedProperty(
                property_id=property.id,
                user_id=seller_id,
                notes=f"Interested in this {prop_data['specs']['property_type']} in {prop_data['address']['city']}"
            )
            db.session.add(saved)

        # Create a dedicated buyer for offers
        buyer_id = uuid4()
        buyer = create_user_with_roles(buyer_id, is_seller=False, is_buyer=True)

        # Create some saved properties
        saved = SavedProperty(
            property_id=specific_property_id,
            user_id=buyer_id,  # Use dedicated buyer
            notes="Great location, need to book viewing"
        )
        db.session.add(saved)

        db.session.commit()
        print("Database reset complete!")

def create_test_users():
    """Create test users"""
    users = [
        User(
            id="test-user-1",  # Changed from uuid4() to string ID
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone_number="+44123456789"
        ),
        User(
            id="test-user-2",  # Changed from uuid4() to string ID
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone_number="+44987654321"
        )
    ]
    # ... rest of function

if __name__ == "__main__":
    reset_database() 