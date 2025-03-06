from app import create_app, db
from app.models import (
    User, Property, Address, PropertySpecs, PropertyMedia, 
    PropertyDetail, PropertyFeatures, UserRole, SavedProperty,
    PropertyNegotiation, OfferTransaction
)

def reset_database():
    """Reset database - drop all tables and create new empty ones"""
    app = create_app('production')
    
    with app.app_context():
        # Log the database URL (masked)
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        masked_url = db_url.replace(db_url.split('@')[0].split(':')[2], '****')
        print(f"Connecting to database: {masked_url}")
        
        # Drop and recreate tables
        print("Dropping all tables...")
        db.drop_all()
        print("Creating new empty tables...")
        db.create_all()
        
        print("Database reset complete! Tables are empty and ready to use.")

if __name__ == "__main__":
    reset_database() 