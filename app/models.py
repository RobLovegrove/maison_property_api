from app import db
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.types import TypeDecorator, CHAR
import uuid


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
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(
        db.String(20), nullable=True
    )  # Nullable as some might not provide phone

    properties = relationship("Property", back_populates="owner")
    roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    saved_properties = relationship(
        "SavedProperty", back_populates="user", cascade="all, delete-orphan"
    )

    # Negotiations relationships
    negotiations_as_buyer = relationship(
        "PropertyNegotiation",
        foreign_keys="[PropertyNegotiation.buyer_id]",
        back_populates="buyer",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


@dataclass
class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(GUID(), ForeignKey("users.id"), nullable=False)
    role_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="roles")

    __table_args__ = (
        db.CheckConstraint(
            "role_type IN ('buyer', 'seller')", name="valid_role_types"
        ),
    )


@dataclass
class Property(db.Model):
    __tablename__ = "properties"
    __allow_unmapped__ = True

    VALID_STATUSES = ["for_sale", "under_offer", "sold"]

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    price = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    main_image_url = db.Column(db.String(500))
    user_id = db.Column(GUID(), ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    last_updated = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    status = db.Column(db.String(20), nullable=False, default="for_sale")

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
    offers = relationship(
        "PropertyOffer",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    saved_by = relationship(
        "SavedProperty",
        back_populates="property",
        cascade="all, delete-orphan",
    )
    negotiations = relationship(
        "PropertyNegotiation",
        back_populates="property",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}", name="valid_property_status"
        ),
    )


@dataclass
class PropertyDetail(db.Model):
    __tablename__ = "property_details"

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    description = db.Column(db.String, nullable=True)
    construction_year = db.Column(db.Integer, nullable=True)
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
        primaryjoin="Address.property_id == Property.id",
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
    image_type = db.Column(db.String, nullable=False, default="image")
    display_order = db.Column(db.Integer, nullable=True)

    property = relationship("Property", back_populates="media")


@dataclass
class PropertyOffer(db.Model):
    __tablename__ = "property_offers"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id"), nullable=False
    )
    buyer_id = db.Column(GUID(), ForeignKey("users.id"), nullable=False)
    offer_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    counter_offer_amount = db.Column(db.Integer)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    property = relationship("Property", back_populates="offers")

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'accepted', 'rejected', 'countered')",
            name="valid_offer_status",
        ),
    )


@dataclass
class SavedProperty(db.Model):
    __tablename__ = "saved_properties"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id"), nullable=False
    )
    user_id = db.Column(GUID(), ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    property = relationship("Property", back_populates="saved_by")
    user = relationship("User", back_populates="saved_properties")

    __table_args__ = (
        db.UniqueConstraint(
            "property_id", "user_id", name="uq_user_saved_property"
        ),
    )


class PropertyNegotiation(db.Model):
    """Model for property negotiations"""

    __tablename__ = "property_negotiations"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(
        GUID(), ForeignKey("properties.id"), nullable=False
    )
    buyer_id = db.Column(GUID(), ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    last_offer_by = db.Column(GUID(), ForeignKey("users.id"), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships - specify foreign_keys explicitly
    property = relationship("Property", back_populates="negotiations")
    buyer = relationship(
        "User", foreign_keys=[buyer_id], back_populates="negotiations_as_buyer"
    )
    last_offer_user = relationship("User", foreign_keys=[last_offer_by])
    transactions = relationship(
        "OfferTransaction",
        back_populates="negotiation",
        order_by="OfferTransaction.created_at",
    )

    VALID_STATUSES = ["active", "accepted", "rejected", "withdrawn", "expired"]

    __table_args__ = (
        db.CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}",
            name="valid_negotiation_status",
        ),
    )


class OfferTransaction(db.Model):
    """Model for individual offers within a negotiation"""

    __tablename__ = "offer_transactions"

    id = db.Column(GUID(), primary_key=True, default=uuid.uuid4)
    negotiation_id = db.Column(
        GUID(), ForeignKey("property_negotiations.id"), nullable=False
    )
    offer_amount = db.Column(db.Integer, nullable=False)
    made_by = db.Column(
        GUID(), ForeignKey("users.id"), nullable=False
    )  # Could be buyer or seller
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    negotiation = relationship(
        "PropertyNegotiation", back_populates="transactions"
    )
    user = relationship("User")
