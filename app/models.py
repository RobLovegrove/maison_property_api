from app import db
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, String
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

    id = db.Column(String(128), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(
        db.String(20), nullable=True
    )  # Nullable as some might not provide phone

    properties = relationship("Property", back_populates="seller")
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(String(128), ForeignKey("users.id"), nullable=False)
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    main_image_url = db.Column(db.String(500))
    seller_id = db.Column(
        String(128), db.ForeignKey("users.id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.now(timezone.utc)
    )
    last_updated = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    status = db.Column(db.String(20), nullable=False, default="for_sale")

    # Address fields (from Address model)
    house_number = db.Column(db.String, nullable=True)
    street = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    postcode = db.Column(db.String, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Specs fields (from PropertySpecs model)
    reception_rooms = db.Column(db.Integer, nullable=True)
    square_footage = db.Column(db.Float, nullable=True)
    property_type = db.Column(db.String, nullable=True)
    epc_rating = db.Column(db.String, nullable=True)

    # Relationships with cascade delete
    seller = relationship("User", back_populates="properties")
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
    features = relationship(
        "PropertyFeatures",
        back_populates="property",
        uselist=False,
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

    def get_address_dict(self):
        """Return address as a dict for backward compatibility"""
        return {
            "house_number": self.house_number,
            "street": self.street,
            "city": self.city,
            "postcode": self.postcode,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def get_specs_dict(self):
        """Return specs as a dict for backward compatibility"""
        return {
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "reception_rooms": self.reception_rooms,
            "square_footage": self.square_footage,
            "property_type": self.property_type,
            "epc_rating": self.epc_rating,
        }


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
class SavedProperty(db.Model):
    __tablename__ = "saved_properties"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    user_id = db.Column(String(128), ForeignKey("users.id"), nullable=False)
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = db.Column(UUID(as_uuid=True), db.ForeignKey("properties.id"))
    buyer_id = db.Column(String(128), db.ForeignKey("users.id"))
    status = db.Column(db.String(20), nullable=False, default="active")
    last_offer_by = db.Column(
        String(128), ForeignKey("users.id"), nullable=True
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Buyer information fields
    buyer_status = db.Column(
        db.String(50), nullable=True
    )  # e.g., "first_time_buyer"
    preferred_move_in_date = db.Column(
        db.String(50), nullable=True
    )  # e.g., "1-3 months"
    payment_method = db.Column(
        db.String(50), nullable=True
    )  # e.g., "mortgage"
    mortgage_status = db.Column(
        db.String(50), nullable=True
    )  # e.g., "mortgage_in_principle"
    additional_notes = db.Column(db.Text, nullable=True)

    # Add new fields for tracking actions
    accepted_by = db.Column(String(128), ForeignKey("users.id"), nullable=True)
    accepted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    rejected_by = db.Column(String(128), ForeignKey("users.id"), nullable=True)
    rejected_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)

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

    # Update valid statuses
    VALID_STATUSES = [
        "active",
        "accepted",
        "rejected",
        "cancelled",
        "withdrawn",
        "expired",
    ]

    __table_args__ = (
        db.CheckConstraint(
            f"status IN {tuple(VALID_STATUSES)}",
            name="valid_negotiation_status",
        ),
    )


class OfferTransaction(db.Model):
    """Model for individual offers within a negotiation"""

    __tablename__ = "offer_transactions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey("property_negotiations.id"),
        nullable=False,
    )
    offer_amount = db.Column(db.Integer, nullable=False)
    made_by = db.Column(String(128), ForeignKey("users.id"), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    negotiation = relationship(
        "PropertyNegotiation", back_populates="transactions"
    )
    user = relationship("User")


class TransactionProgress(db.Model):
    """Model for tracking transaction progress after offer acceptance"""

    __tablename__ = "transaction_progress"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = db.Column(
        UUID(as_uuid=True),
        ForeignKey("property_negotiations.id"),
        nullable=False,
    )

    # Mortgage Information
    mortgage_decision = db.Column(
        db.String(20), nullable=True
    )  # "mortgage" or "cash"
    mortgage_provider = db.Column(db.String(100), nullable=True)
    mortgage_provider_submitted = db.Column(db.Boolean, default=False)
    onsite_visit_required = db.Column(
        db.String(10), nullable=True
    )  # "yes", "no", null
    mortgage_valuation_schedule_date = db.Column(db.Date, nullable=True)
    mortgage_valuation_schedule_time = db.Column(db.Time, nullable=True)
    mortgage_valuation_visit_completed = db.Column(db.Boolean, default=False)
    mortgage_offer_file_url = db.Column(db.String(500), nullable=True)
    mortgage_offer_file_name = db.Column(db.String(255), nullable=True)

    # Property Survey
    property_survey_decision = db.Column(
        db.String(10), nullable=True
    )  # "yes", "no", null
    surveyor_name = db.Column(db.String(100), nullable=True)
    surveyor_email = db.Column(db.String(120), nullable=True)
    surveyor_phone = db.Column(db.String(20), nullable=True)
    survey_schedule_date = db.Column(db.Date, nullable=True)
    survey_schedule_time = db.Column(db.Time, nullable=True)
    survey_visit_completed = db.Column(db.Boolean, default=False)
    survey_approval = db.Column(
        db.String(20), nullable=True
    )  # "pending", "approved", "rejected", null

    # Conveyancing
    buyer_solicitor_name = db.Column(db.String(100), nullable=True)
    buyer_solicitor_contact = db.Column(db.String(120), nullable=True)
    seller_solicitor_name = db.Column(db.String(100), nullable=True)
    seller_solicitor_contact = db.Column(db.String(120), nullable=True)

    # Final Checks, Exchange, Completion
    buyer_final_checks_confirmed = db.Column(db.Boolean, default=False)
    seller_final_checks_confirmed = db.Column(db.Boolean, default=False)
    buyer_exchange_contracts_confirmed = db.Column(db.Boolean, default=False)
    seller_exchange_contracts_confirmed = db.Column(db.Boolean, default=False)
    buyer_completion_confirmed = db.Column(db.Boolean, default=False)
    seller_completion_confirmed = db.Column(db.Boolean, default=False)

    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    negotiation = relationship(
        "PropertyNegotiation", backref="transaction_progress"
    )

    __table_args__ = (
        db.CheckConstraint(
            "mortgage_decision IN ('mortgage', 'cash')",
            name="valid_mortgage_decision",
        ),
        db.CheckConstraint(
            "onsite_visit_required IN ('yes', 'no')",
            name="valid_onsite_visit_required",
        ),
        db.CheckConstraint(
            "property_survey_decision IN ('yes', 'no')",
            name="valid_property_survey_decision",
        ),
        db.CheckConstraint(
            "survey_approval IN ('pending', 'approved', 'rejected')",
            name="valid_survey_approval",
        ),
    )
