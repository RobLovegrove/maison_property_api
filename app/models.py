from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

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

    __tablename__ = 'properties'

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