from marshmallow import Schema, fields, validate, EXCLUDE
from app.models import Property


# Define base schemas first
class UserRoleSchema(Schema):
    """Schema for user role validation and serialization"""

    role_type = fields.Str(
        required=True, validate=validate.OneOf(["buyer", "seller"])
    )


class UserSchema(Schema):
    """Schema for basic user data"""

    class Meta:
        unknown = EXCLUDE

    user_id = fields.UUID(dump_only=True, attribute="id")
    first_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    last_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    phone_number = fields.Str(
        validate=validate.Length(max=20), allow_none=True
    )
    full_name = fields.Str(dump_only=True)
    roles = fields.Nested(UserRoleSchema, many=True, dump_only=True)


class AddressSchema(Schema):
    """Schema for address data"""

    class Meta:
        unknown = EXCLUDE

    house_number = fields.Str(required=True)
    street = fields.Str(required=True)
    city = fields.Str(required=True)
    postcode = fields.Str(required=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)


class PropertySpecsSchema(Schema):
    """Schema for property specifications"""

    class Meta:
        unknown = EXCLUDE

    bedrooms = fields.Int(required=True, validate=validate.Range(min=0))
    bathrooms = fields.Int(required=True, validate=validate.Range(min=0))
    reception_rooms = fields.Int(required=True, validate=validate.Range(min=0))
    square_footage = fields.Float(
        required=True, validate=validate.Range(min=0), allow_none=False
    )
    property_type = fields.Str(required=True)
    epc_rating = fields.Str(required=True)


class PropertySchema(Schema):
    """Schema for property data"""

    class Meta:
        unknown = EXCLUDE

    property_id = fields.UUID(dump_only=True, attribute="id")
    price = fields.Integer(required=True)
    bedrooms = fields.Integer()
    bathrooms = fields.Float()
    main_image_url = fields.String(allow_none=True)
    image_urls = fields.List(fields.String(), allow_none=True)
    floorplan_url = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    seller_id = fields.UUID(required=True, attribute="user_id")
    status = fields.String(
        validate=validate.OneOf(Property.VALID_STATUSES),
        required=True,
        default="for_sale",
    )
    address = fields.Nested(AddressSchema)
    specs = fields.Nested(PropertySpecsSchema)
    offers = fields.Nested("PropertyOfferSchema", many=True, dump_only=True)
    saved_by_count = fields.Method("get_saved_by_count", dump_only=True)

    def get_saved_by_count(self, obj):
        return len(obj.saved_by) if obj.saved_by else 0


class PropertyListSchema(Schema):
    """Schema for property list response"""

    class Meta:
        unknown = EXCLUDE

    def get_property_id(self, obj):
        """Get ID as string"""
        if not obj:
            return None
        return str(obj.id) if hasattr(obj, "id") else str(obj)

    property_id = fields.Method("get_property_id", required=True)
    price = fields.Int(required=True)
    bedrooms = fields.Int()
    bathrooms = fields.Int()
    main_image_url = fields.URL(allow_none=True)
    created_at = fields.DateTime(format="iso")
    seller_id = fields.UUID(required=True, attribute="seller_id")
    address = fields.Nested(
        AddressSchema(only=("street", "city", "postcode")), dump_only=True
    )
    specs = fields.Nested(
        PropertySpecsSchema(only=("property_type", "square_footage")),
        dump_only=True,
    )


class OfferTransactionSchema(Schema):
    """Schema for individual offer transactions within a negotiation"""

    transaction_id = fields.UUID(dump_only=True, attribute="id")
    offer_amount = fields.Integer(
        required=True, validate=validate.Range(min=0)
    )
    made_by = fields.UUID(
        required=True
    )  # User ID of who made this offer (buyer or seller)
    created_at = fields.DateTime(dump_only=True)


class PropertyNegotiationSchema(Schema):
    """Schema for property offer negotiations"""

    negotiation_id = fields.UUID(dump_only=True, attribute="id")
    property_id = fields.UUID(required=True)
    buyer_id = fields.UUID(required=True)
    last_offer_by = fields.UUID(
        dump_only=True
    )  # ID of user who made the last offer
    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf(
            [
                "active",  # Negotiation is ongoing
                "accepted",  # Final offer was accepted
                "rejected",  # Final offer was rejected
                "withdrawn",  # Buyer withdrew from negotiations
                "expired",  # Negotiation expired without conclusion
            ]
        ),
    )
    transactions = fields.Nested(OfferTransactionSchema, many=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    current_offer = fields.Method(
        "get_current_offer"
    )  # Latest offer in the chain
    awaiting_response_from = fields.Method(
        "get_awaiting_response_from"
    )  # Who needs to respond next

    def get_current_offer(self, obj):
        """Get the most recent offer amount"""
        if obj.transactions:
            return sorted(obj.transactions, key=lambda x: x.created_at)[
                -1
            ].offer_amount
        return None

    def get_awaiting_response_from(self, obj):
        """Determine who needs to respond next"""
        if obj.status != "active" or not obj.last_offer_by:
            return None
        # If buyer made last offer, seller needs to respond (property owner)
        return "seller" if obj.last_offer_by == obj.buyer_id else "buyer"


class SavedPropertyDashboardSchema(Schema):
    """Schema for saved properties in dashboard"""

    class Meta:
        unknown = EXCLUDE

    property_id = fields.UUID(required=True)
    price = fields.Int(required=True)
    status = fields.Str(required=True)
    main_image_url = fields.URL(allow_none=True)
    notes = fields.Str(allow_none=True)
    saved_at = fields.DateTime(format="iso")
    address = fields.Nested(
        AddressSchema(only=("street", "city", "postcode")), dump_only=True
    )
    specs = fields.Nested(
        PropertySpecsSchema(only=("bedrooms", "bathrooms", "property_type")),
        dump_only=True,
    )


class UserDashboardSchema(Schema):
    """Schema for user dashboard response"""

    class Meta:
        unknown = EXCLUDE

    user = fields.Nested(
        UserSchema(
            only=(
                "user_id",
                "first_name",
                "last_name",
                "email",
                "phone_number",
            )
        )
    )
    roles = fields.Nested("UserRoleSchema", many=True)
    listed_properties = fields.Nested(PropertyListSchema, many=True)
    saved_properties = fields.Nested(SavedPropertyDashboardSchema, many=True)
    negotiations_as_buyer = fields.Nested(
        "PropertyNegotiationSchema", many=True
    )
    negotiations_as_seller = fields.Nested(
        "PropertyNegotiationSchema", many=True
    )
    total_properties_listed = fields.Method("get_total_properties")
    total_saved_properties = fields.Method("get_total_saved")

    def get_total_properties(self, obj):
        return len(obj.get("listed_properties", []))

    def get_total_saved(self, obj):
        return len(obj.get("saved_properties", []))


# Create and Update schemas
class UserCreateSchema(Schema):
    """Schema for creating a new user"""

    class Meta:
        unknown = EXCLUDE

    user_id = fields.UUID(required=True)
    first_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    last_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    phone_number = fields.Str(
        validate=validate.Length(max=20), allow_none=True
    )
    roles = fields.List(fields.Nested(UserRoleSchema), required=False)


class UserUpdateSchema(UserSchema):
    class Meta:
        unknown = EXCLUDE

    first_name = fields.Str(validate=validate.Length(min=1, max=50))
    last_name = fields.Str(validate=validate.Length(min=1, max=50))
    email = fields.Email(validate=validate.Length(max=120))


class PropertyUpdateSchema(Schema):
    """Schema for property updates"""

    class Meta:
        unknown = EXCLUDE

    price = fields.Integer(validate=validate.Range(min=0), required=False)
    status = fields.String(
        validate=validate.OneOf(["for_sale", "under_offer", "sold"]),
        required=False,
    )
    specs = fields.Nested(PropertySpecsSchema, partial=True, required=False)


class PropertyFeaturesSchema(Schema):
    """Schema for property features"""

    class Meta:
        unknown = EXCLUDE

    has_garden = fields.Bool(default=False)
    garden_size = fields.Float(allow_none=True)
    parking_spaces = fields.Int(default=0)
    has_garage = fields.Bool(default=False)


class PropertyDetailsSchema(Schema):
    """Schema for property details"""

    class Meta:
        unknown = EXCLUDE

    description = fields.Str(required=True)
    construction_year = fields.Int(required=True)
    heating_type = fields.Str(required=True)


class PropertyMediaSchema(Schema):
    """Schema for property media"""

    class Meta:
        unknown = EXCLUDE

    image_url = fields.URL(required=True)
    image_type = fields.Str(default="interior")
    is_main_image = fields.Bool(default=False)
    display_order = fields.Int(allow_none=True)


class PropertyCreateSchema(Schema):
    """Schema for creating a new property"""

    class Meta:
        unknown = EXCLUDE

    price = fields.Int(required=True, validate=validate.Range(min=0))
    main_image_url = fields.URL(allow_none=True)
    address = fields.Nested(AddressSchema, required=True)
    specs = fields.Nested(PropertySpecsSchema, required=True)
    features = fields.Nested(PropertyFeaturesSchema, required=False)
    details = fields.Nested(PropertyDetailsSchema, required=False)
    media = fields.List(fields.Nested(PropertyMediaSchema), required=False)
    seller_id = fields.UUID(required=True, attribute="user_id")
    status = fields.String(
        validate=validate.OneOf(Property.VALID_STATUSES),
        required=False,
        default="for_sale",
        description="Property status (defaults to 'for_sale')",
    )


class PropertyOfferSchema(Schema):
    """Schema for property offer validation and serialization"""

    offer_id = fields.UUID(dump_only=True, attribute="id")
    property_id = fields.UUID(required=True)
    buyer_id = fields.UUID(required=True)
    offer_amount = fields.Integer(
        required=True, validate=validate.Range(min=0)
    )
    status = fields.Str(dump_only=True)  # Only API can update status
    counter_offer_amount = fields.Integer(validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class SavedPropertySchema(Schema):
    """Schema for saved property validation and serialization"""

    id = fields.UUID(dump_only=True)
    property_id = fields.UUID(required=True)
    user_id = fields.UUID(required=True)
    notes = fields.Str(allow_none=True)  # Explicitly mark as optional
    created_at = fields.DateTime(dump_only=True)


class UserCountsSchema(Schema):
    """Schema for user role counts"""

    class Meta:
        unknown = EXCLUDE

    total_buyers = fields.Int(required=True)
    total_sellers = fields.Int(required=True)
    total_unique_users = fields.Int(required=True)


class UsersListSchema(Schema):
    """Schema for users list response"""

    class Meta:
        unknown = EXCLUDE

    sellers = fields.List(fields.UUID(), required=True)
    buyers = fields.List(fields.UUID(), required=True)
    counts = fields.Nested(UserCountsSchema, required=True)
