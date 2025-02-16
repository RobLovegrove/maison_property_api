#!/usr/bin/env python

from app import create_app, db
from app.models import Property, Address, PropertySpecs, PropertyFeatures, User
from datetime import datetime, timedelta, UTC
import random

app = create_app()

# Sample data for generating properties
CITIES = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Bristol']
STREETS = ['High Street', 'Station Road', 'Church Lane', 'Victoria Road', 'Green Street']
PROPERTY_TYPES = ['detached', 'semi-detached', 'terraced', 'flat', 'bungalow']
EPC_RATINGS = ['A', 'B', 'C', 'D', 'E']

# Add sample users
USERS = [
    {"email": "john.smith@example.com", "name": "John Smith"},
    {"email": "sarah.jones@example.com", "name": "Sarah Jones"},
    {"email": "mike.wilson@example.com", "name": "Mike Wilson"}
]

# Update sample image data with more realistic URLs
SAMPLE_IMAGES = [
    "https://maison-property-images.azurewebsites.net/properties/modern-house-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/luxury-apartment-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/garden-view-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/kitchen-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/living-room-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/bedroom-master-1.jpg",
    "https://maison-property-images.azurewebsites.net/properties/bathroom-1.jpg",
]

SAMPLE_FLOORPLANS = [
    "https://maison-property-images.azurewebsites.net/floorplans/2-bed-flat.pdf",
    "https://maison-property-images.azurewebsites.net/floorplans/3-bed-house.pdf",
    "https://maison-property-images.azurewebsites.net/floorplans/4-bed-detached.pdf",
]

def generate_postcode(city):
    """Generate a realistic UK postcode"""
    areas = {
        'London': ['SW', 'SE', 'N', 'E', 'W'],
        'Manchester': ['M'],
        'Birmingham': ['B'],
        'Leeds': ['LS'],
        'Bristol': ['BS']
    }
    area = random.choice(areas.get(city, ['XX']))
    return f"{area}{random.randint(1,20)} {random.randint(1,9)}{random.choice('ABCDEFGHIJKLNPQRSTUVWXYZ')}Z"

def create_sample_properties(num_properties=10):
    """Create sample properties with realistic data"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create users first
        users = []
        for user_data in USERS:
            user = User(**user_data)
            db.session.add(user)
            users.append(user)
        
        for i in range(num_properties):
            # Generate basic property data
            city = random.choice(CITIES)
            bedrooms = random.randint(1, 5)
            # Price based on bedrooms and city
            base_price = 200000 + (bedrooms * 50000)
            if city == 'London':
                base_price *= 2
                
            # Create property
            now = datetime.now(UTC)
            property = Property(
                price=base_price,
                status='for_sale',
                description=f"A lovely {bedrooms} bedroom property in {city}",
                created_at=now - timedelta(days=random.randint(0, 30)),
                last_updated=now,
                ownership_type=random.choice(['freehold', 'leasehold']),
                key_features=[
                    "Recently renovated",
                    "Close to transport",
                    "Modern kitchen",
                    "South-facing garden" if random.random() > 0.5 else "Private parking"
                ],
                council_tax_band=random.choice(['A', 'B', 'C', 'D', 'E']),
                main_image_url=random.choice(SAMPLE_IMAGES),
                additional_image_urls=[
                    random.choice(SAMPLE_IMAGES) 
                    for _ in range(random.randint(3, 6))  # 3-6 additional images
                ],
                floorplan_url=random.choice(SAMPLE_FLOORPLANS)
            )
            db.session.add(property)
            
            # Create address
            address = Address(
                property=property,
                house_number=str(random.randint(1, 200)),
                street=random.choice(STREETS),
                city=city,
                postcode=generate_postcode(city)
            )
            db.session.add(address)
            
            # Create specs
            specs = PropertySpecs(
                property=property,
                bedrooms=bedrooms,
                bathrooms=max(1, bedrooms - 1),
                reception_rooms=random.randint(1, 3),
                square_footage=float(bedrooms * 200 + random.randint(400, 800)),
                property_type=random.choice(PROPERTY_TYPES),
                epc_rating=random.choice(EPC_RATINGS)
            )
            db.session.add(specs)
            
            # Create features
            features = PropertyFeatures(
                property=property,
                has_garden=random.random() > 0.3,
                garden_size=random.randint(20, 200) if random.random() > 0.3 else None,
                parking_spaces=random.randint(0, 3),
                has_garage=random.random() > 0.7
            )
            db.session.add(features)
            
            # Assign random user as owner
            property.owner = random.choice(users)
        
        db.session.commit()
        print(f"Created {num_properties} sample properties")

if __name__ == "__main__":
    create_sample_properties()
