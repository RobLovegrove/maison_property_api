from app import db
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship


@dataclass
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    properties: Mapped[List["Property"]] = relationship(back_populates="owner")


@dataclass
class Property(db.Model):
    __tablename__ = "properties"
    __allow_unmapped__ = True  # Allow legacy annotations

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[int]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), index=True  # Add index for performance
    )
    last_updated: Mapped[datetime] = mapped_column(
        default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )
    address: Mapped["Address"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    specs: Mapped["PropertySpecs"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    features: Mapped["PropertyFeatures"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    media: Mapped[List["PropertyMedia"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    description: Mapped[str]
    main_image_url: Mapped[Optional[str]]  # For list view
    additional_image_urls: Mapped[Optional[List[str]]] = mapped_column(db.JSON)
    floorplan_url: Mapped[Optional[str]]
    ownership_type: Mapped[str]
    leasehold_remaining: Mapped[Optional[int]]
    property_age: Mapped[Optional[str]]
    key_features: Mapped[List[str]] = mapped_column(db.JSON)
    council_tax_band: Mapped[str]
    user_id: Mapped[Optional[int]] = mapped_column(db.ForeignKey("users.id"))
    owner: Mapped[Optional["User"]] = relationship(back_populates="properties")


@dataclass
class Address(db.Model):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(db.ForeignKey("properties.id"))
    house_number: Mapped[str]
    street: Mapped[str]
    city: Mapped[str]
    postcode: Mapped[str]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]

    property: Mapped["Property"] = relationship(back_populates="address")


@dataclass
class PropertySpecs(db.Model):
    __tablename__ = "property_specs"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(db.ForeignKey("properties.id"))
    bedrooms: Mapped[int]
    bathrooms: Mapped[int]
    reception_rooms: Mapped[int]
    square_footage: Mapped[float]
    property_type: Mapped[str]
    epc_rating: Mapped[str]

    property: Mapped["Property"] = relationship(back_populates="specs")


@dataclass
class PropertyFeatures(db.Model):
    __tablename__ = "property_features"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(db.ForeignKey("properties.id"))
    has_garden: Mapped[bool] = mapped_column(default=False)
    garden_size: Mapped[Optional[float]]
    parking_spaces: Mapped[int] = mapped_column(default=0)
    has_garage: Mapped[bool] = mapped_column(default=False)

    property: Mapped["Property"] = relationship(back_populates="features")


@dataclass
class PropertyMedia(db.Model):
    __tablename__ = "property_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(db.ForeignKey("properties.id"))
    image_url: Mapped[str]
    is_main_image: Mapped[bool] = mapped_column(default=False)
    image_type: Mapped[Optional[str]]

    property: Mapped["Property"] = relationship(back_populates="media")
