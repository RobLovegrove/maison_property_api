from app import db
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.types import TypeDecorator, CHAR
import uuid


@dataclass
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    properties = relationship("Property", back_populates="owner")


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), store as stringified
    hex values.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


@dataclass
class Property(db.Model):
    __tablename__ = "properties"
    __allow_unmapped__ = True

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    price = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    main_image_url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    last_updated = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships with cascade delete
    address = relationship(
        "Address",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )
    owner = relationship("User", back_populates="properties")
    media = relationship(
        "PropertyMedia",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    details = relationship(
        "PropertyDetail",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )
    specs = relationship(
        "PropertySpecs",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )
    features = relationship(
        "PropertyFeatures",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )


@dataclass
class PropertyDetail(db.Model):
    __tablename__ = "property_details"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    description = db.Column(db.String, nullable=True)
    property_type = db.Column(db.String, nullable=True)
    construction_year = db.Column(db.Integer, nullable=True)
    parking_spaces = db.Column(db.Integer, nullable=True)
    heating_type = db.Column(db.String, nullable=True)

    property = relationship("Property", back_populates="details")


@dataclass
class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    house_number = db.Column(db.String, nullable=False)
    street = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    property = relationship(
        "Property",
        back_populates="address",
        primaryjoin="Address.property_id == Property.id"
    )


@dataclass
class PropertySpecs(db.Model):
    __tablename__ = "property_specs"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    reception_rooms = db.Column(db.Integer, nullable=False)
    square_footage = db.Column(db.Float, nullable=False)
    property_type = db.Column(db.String, nullable=False)
    epc_rating = db.Column(db.String, nullable=False)

    property: Mapped["Property"] = relationship(back_populates="specs")


@dataclass
class PropertyFeatures(db.Model):
    __tablename__ = "property_features"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    has_garden = db.Column(db.Boolean, default=False)
    garden_size = db.Column(db.Float, nullable=True)
    parking_spaces = db.Column(db.Integer, default=0)
    has_garage = db.Column(db.Boolean, default=False)

    property = relationship("Property", back_populates="features")


@dataclass
class PropertyMedia(db.Model):
    __tablename__ = "property_media"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    image_url = db.Column(db.String, nullable=False)
    image_type = db.Column(db.String, nullable=False)
    display_order = db.Column(db.Integer, nullable=True)

    property = relationship("Property", back_populates="media")
