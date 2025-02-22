from marshmallow import Schema, fields, validate, EXCLUDE


class AddressSchema(Schema):
    """Schema for validating and serializing address data"""

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
        required=True, validate=validate.Range(min=0)
    )
    property_type = fields.Str(required=True)
    epc_rating = fields.Str(required=True)


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
    property_type = fields.Str(required=True)
    construction_year = fields.Int(required=True)
    parking_spaces = fields.Int(required=True)
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
    user_id = fields.Int(required=True)
    address = fields.Nested(AddressSchema, required=True)
    specs = fields.Nested(PropertySpecsSchema, required=True)
    features = fields.Nested(PropertyFeaturesSchema, required=False)
    details = fields.Nested(PropertyDetailsSchema, required=False)
    media = fields.List(fields.Nested(PropertyMediaSchema), required=False)


class PropertyUpdateSchema(Schema):
    """Schema for updating an existing property"""

    class Meta:
        unknown = EXCLUDE

    price = fields.Int(validate=validate.Range(min=0))
    main_image_url = fields.URL(allow_none=True)
    address = fields.Nested(AddressSchema)
    specs = fields.Nested(PropertySpecsSchema)
    features = fields.Nested(PropertyFeaturesSchema)
    details = fields.Nested(PropertyDetailsSchema)
    media = fields.List(fields.Nested(PropertyMediaSchema))


class PropertyListSchema(Schema):
    """Schema for property list response"""

    class Meta:
        unknown = EXCLUDE

    id = fields.UUID(required=True)
    price = fields.Int(required=True)
    bedrooms = fields.Int()
    bathrooms = fields.Int()
    main_image_url = fields.URL(allow_none=True)
    created_at = fields.DateTime(format="iso")
    owner_id = fields.Int(
        required=True
    )  # Just the ID, not the full user object
    address = fields.Nested(AddressSchema(only=("street", "city", "postcode")))
    specs = fields.Nested(
        PropertySpecsSchema(only=("property_type", "square_footage"))
    )
