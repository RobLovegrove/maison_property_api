from app import db
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import UUIDType


@dataclass
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc)
    )
    properties: Mapped[List["Property"]] = relationship(back_populates="owner")


@dataclass
class Property(db.Model):
    __tablename__ = "properties"
    __allow_unmapped__ = True

    id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), primary_key=True, default=uuid4
    )
    price: Mapped[int]
    bedrooms: Mapped[int]
    bathrooms: Mapped[float]
    main_image_url: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc)
    )
    last_updated: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )

    # Relationships
    address: Mapped["Address"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    owner: Mapped[Optional["User"]] = relationship(back_populates="properties")
    media: Mapped[List["PropertyMedia"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    details: Mapped["PropertyDetail"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    specs: Mapped["PropertySpecs"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    features: Mapped["PropertyFeatures"] = relationship(
        back_populates="property", uselist=False, cascade="all, delete-orphan"
    )


class PropertyDetail(db.Model):
    __tablename__ = "property_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False),
        db.ForeignKey("properties.id"),
        nullable=False,
        unique=True,
    )
    description: Mapped[Optional[str]]
    property_type: Mapped[Optional[str]]
    construction_year: Mapped[Optional[int]]
    parking_spaces: Mapped[Optional[int]]
    heating_type: Mapped[Optional[str]]

    property: Mapped["Property"] = relationship(back_populates="details")


@dataclass
class Address(db.Model):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), db.ForeignKey("properties.id"), unique=True
    )
    house_number: Mapped[str]
    street: Mapped[str]
    city: Mapped[str]
    postcode: Mapped[str]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]

    property: Mapped["Property"] = relationship(
        back_populates="address", foreign_keys=[property_id]
    )


@dataclass
class PropertySpecs(db.Model):
    __tablename__ = "property_specs"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), db.ForeignKey("properties.id")
    )
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
    property_id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), db.ForeignKey("properties.id")
    )
    has_garden: Mapped[bool] = mapped_column(default=False)
    garden_size: Mapped[Optional[float]]
    parking_spaces: Mapped[int] = mapped_column(default=0)
    has_garage: Mapped[bool] = mapped_column(default=False)

    property: Mapped["Property"] = relationship(back_populates="features")


@dataclass
class PropertyMedia(db.Model):
    __tablename__ = "property_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[UUID] = mapped_column(
        UUIDType(binary=False), db.ForeignKey("properties.id")
    )
    image_url: Mapped[str]
    image_type: Mapped[str]  # e.g., 'additional', 'floorplan'
    display_order: Mapped[Optional[int]]  # For ordering additional images

    property: Mapped["Property"] = relationship(back_populates="media")
