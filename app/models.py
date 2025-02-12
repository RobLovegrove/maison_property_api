from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from typing import List

db = SQLAlchemy()


@dataclass
class Property(db.Model):
    id: int
    price: int
    address: str
    bedrooms: int
    bathrooms: int
    reception_rooms: int
    square_footage: float
    property_type: str
    epc_rating: str
    main_image_url: str
    description: str
    additional_image_urls: List[str]
    floorplan_url: str
    ownership_type: str
    leasehold_years_remaining: int
    property_age: str
    key_features: List[str]
    council_tax_band: str

    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    reception_rooms = db.Column(db.Integer, nullable=False)
    square_footage = db.Column(db.Float, nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    epc_rating = db.Column(db.String(2), nullable=False)
    main_image_url = db.Column(db.String(255), nullable=False)

    # New fields
    description = db.Column(db.Text, nullable=False)
    additional_image_urls = db.Column(
        db.JSON, nullable=True
    )  # Optional - might not have additional images
    floorplan_url = db.Column(
        db.String(255), nullable=True
    )  # Optional - might not have floorplan
    ownership_type = db.Column(
        db.String(50), nullable=False
    )  # Required - freehold/leasehold is important
    leasehold_years_remaining = db.Column(
        db.Integer, nullable=True
    )  # Optional - only for leaseholds
    property_age = db.Column(
        db.String(100), nullable=True
    )  # Optional - might be unknown
    key_features = db.Column(
        db.JSON, nullable=False
    )  # Required - every property should have key features
    council_tax_band = db.Column(
        db.String(1), nullable=False
    )  # Required - every property has a council tax band
