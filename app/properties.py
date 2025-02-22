from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    PropertyFeatures,
    PropertyMedia,
    PropertyDetail,
    User,
)
from datetime import datetime, UTC
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
from flask_caching import Cache
from app.schemas import (
    PropertyCreateSchema,
    PropertyUpdateSchema,
    PropertyListSchema,
)
from marshmallow import ValidationError
from app.utils import geocode_address
from app.exceptions import GeocodeError, UserNotFoundError
from sqlalchemy.exc import IntegrityError

bp = Blueprint("properties", __name__)

# Initialize cache in __init__.py
cache = Cache(
    config={
        "CACHE_TYPE": "simple",  # For development
        "CACHE_DEFAULT_TIMEOUT": 300,  # 5 minutes
    }
)


def validate_property_data(data):
    """Validate property data from request."""
    errors = []

    # Validate main property data
    if "price" not in data or not isinstance(data["price"], int):
        errors.append("Price must be a number")

    # Validate address
    if "address" not in data:
        errors.append("Address is required")
    else:
        addr = data["address"]
        required_addr_fields = ["house_number", "street", "city", "postcode"]
        for field in required_addr_fields:
            if field not in addr:
                errors.append(f"Address {field} is required")

    # Validate specs
    if "specs" not in data:
        errors.append("Property specifications are required")
    else:
        specs = data["specs"]
        required_specs = {
            "bedrooms": int,
            "bathrooms": int,
            "reception_rooms": int,
            "square_footage": float,
            "property_type": str,
            "epc_rating": str,
        }
        for field, field_type in required_specs.items():
            if field not in specs:
                errors.append(f"Spec {field} is required")
            elif not isinstance(specs[field], field_type):
                errors.append(f"{field} must be a {field_type.__name__}")

    # Validate details if provided
    if "details" in data:
        details = data["details"]
        required_details = {
            "description": str,
            "property_type": str,
            "construction_year": int,
            "parking_spaces": int,
            "heating_type": str,
        }
        for field, field_type in required_details.items():
            if field not in details:
                errors.append(f"Detail {field} is required")
            elif not isinstance(details[field], field_type):
                errors.append(f"{field} must be a {field_type.__name__}")

    return errors


@bp.route("", methods=["GET"])
def get_properties():
    """List view - returns basic property info with main image only."""
    try:
        query = select(Property).join(Property.address).join(Property.specs)

        # Apply filters
        if request.args.get("min_price"):
            query = query.filter(
                Property.price >= int(request.args.get("min_price"))
            )
        if request.args.get("min_square_footage"):
            query = query.filter(
                PropertySpecs.square_footage
                >= float(request.args.get("min_square_footage"))
            )
        if request.args.get("bathrooms"):
            query = query.filter(
                PropertySpecs.bathrooms >= int(request.args.get("bathrooms"))
            )
        if request.args.get("epc_rating"):
            query = query.filter(
                PropertySpecs.epc_rating == request.args.get("epc_rating")
            )
        if request.args.get("has_garage"):
            query = query.join(Property.features).filter(
                PropertyFeatures.has_garage.is_(True)
            )
        if request.args.get("has_garden"):
            query = query.join(Property.features).filter(
                PropertyFeatures.has_garden.is_(True)
            )
        if request.args.get("postcode_area"):
            query = query.filter(
                Address.postcode.like(f"{request.args.get('postcode_area')}%")
            )

        # Add eager loading and ordering
        query = query.options(
            joinedload(Property.address), joinedload(Property.specs)
        ).order_by(Property.created_at.desc(), Property.id.desc())

        properties = list(db.session.execute(query).scalars())

        # Serialize response using schema
        schema = PropertyListSchema(many=True)
        return jsonify(schema.dump(properties))

    except Exception as e:
        current_app.logger.error(f"Error in get_properties: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/<uuid:property_id>", methods=["GET"])
def get_property(property_id):
    """Get a single property by ID."""
    property_item = db.session.get(Property, property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404

    # Return property data with just owner_id
    return (
        jsonify(
            {
                "id": str(property_item.id),
                "price": property_item.price,
                "bedrooms": property_item.bedrooms,
                "bathrooms": property_item.bathrooms,
                "main_image_url": property_item.main_image_url,
                "created_at": property_item.created_at.isoformat(),
                "owner_id": property_item.user_id,  # Just return the ID
                "address": {
                    "house_number": property_item.address.house_number,
                    "street": property_item.address.street,
                    "city": property_item.address.city,
                    "postcode": property_item.address.postcode,
                    "latitude": property_item.address.latitude,
                    "longitude": property_item.address.longitude,
                },
                "specs": {
                    "bedrooms": property_item.specs.bedrooms,
                    "bathrooms": property_item.specs.bathrooms,
                    "reception_rooms": property_item.specs.reception_rooms,
                    "square_footage": property_item.specs.square_footage,
                    "property_type": property_item.specs.property_type,
                    "epc_rating": property_item.specs.epc_rating,
                },
            }
        ),
        200,
    )


@bp.route("", methods=["POST"])
def create_property():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Validate input data using marshmallow
    schema = PropertyCreateSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return (
            jsonify({"error": "Validation error", "details": err.messages}),
            400,
        )

    try:
        # Verify user exists
        user = db.session.get(User, validated_data["user_id"])
        if not user:
            raise UserNotFoundError(
                f"User {validated_data['user_id']} not found"
            )

        # Create property with bedrooms/bathrooms from specs
        property = Property(
            price=validated_data["price"],
            main_image_url=validated_data.get("main_image_url"),
            user_id=validated_data["user_id"],
            bedrooms=validated_data["specs"]["bedrooms"],
            bathrooms=validated_data["specs"]["bathrooms"],
            created_at=datetime.now(UTC),
            last_updated=datetime.now(UTC),
        )
        db.session.add(property)

        # Get address data and coordinates
        addr_data = validated_data["address"]
        try:
            lat, lon = geocode_address(
                addr_data["house_number"],
                addr_data["street"],
                addr_data["city"],
                addr_data["postcode"],
            )
        except GeocodeError as e:
            current_app.logger.warning(f"Geocoding failed: {str(e)}")
            lat, lon = None, None

        # Create address
        address = Address(
            property=property, **addr_data, latitude=lat, longitude=lon
        )
        db.session.add(address)

        # Create specs
        specs = PropertySpecs(property=property, **validated_data["specs"])
        db.session.add(specs)

        # Create optional related objects
        if "features" in validated_data:
            features = PropertyFeatures(
                property=property, **validated_data["features"]
            )
            db.session.add(features)

        if "details" in validated_data:
            details = PropertyDetail(
                property=property, **validated_data["details"]
            )
            db.session.add(details)

        if "media" in validated_data:
            for media_item in validated_data["media"]:
                media = PropertyMedia(property=property, **media_item)
                db.session.add(media)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Database integrity error: {str(e)}")
            return (
                jsonify(
                    {
                        "error": "Database error",
                        "message": (
                            "Could not create property "
                            "due to data constraints"
                        ),
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "id": property.id,
                    "message": "Property created successfully",
                    "warnings": (
                        [] if (lat and lon) else ["Could not geocode address"]
                    ),
                }
            ),
            201,
        )

    except UserNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except GeocodeError as e:
        return jsonify({"error": "Geocoding error", "message": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Unexpected error creating property: {str(e)}"
        )
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                }
            ),
            500,
        )


@bp.route("/<uuid:property_id>", methods=["PUT"])
def update_property(property_id):
    """Update a property."""
    property_item = db.session.get(Property, property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404

    data = request.get_json()

    # Validate update data
    schema = PropertyUpdateSchema()
    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        # Update main property
        for key, value in validated_data.items():
            if key not in ("address", "specs", "features", "details", "media"):
                setattr(property_item, key, value)

        # Update related objects
        if "address" in validated_data and property_item.address:
            for key, value in validated_data["address"].items():
                setattr(property_item.address, key, value)

        if "specs" in validated_data and property_item.specs:
            for key, value in validated_data["specs"].items():
                setattr(property_item.specs, key, value)

        if "features" in validated_data and property_item.features:
            for key, value in validated_data["features"].items():
                setattr(property_item.features, key, value)

        db.session.commit()
        return jsonify({"message": "Property updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/<uuid:property_id>", methods=["DELETE"])
def delete_property(property_id):
    """Delete a property."""
    property_item = db.session.get(Property, property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404

    try:
        # SQLAlchemy will handle cascade deletes for related tables
        db.session.delete(property_item)
        db.session.commit()
        return jsonify({"message": "Property deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_properties(user_id):
    """Get all properties for a specific user."""
    # Check if user exists
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    # Get all properties for this user
    properties = Property.query.filter_by(user_id=user_id).all()

    # Use the PropertyListSchema to format the response
    schema = PropertyListSchema(many=True)
    return jsonify(schema.dump(properties)), 200
