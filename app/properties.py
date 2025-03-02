from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    PropertyMedia,
)
from datetime import datetime, UTC
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload
from flask_caching import Cache
from app.utils import geocode_address
from app.exceptions import GeocodeError
from uuid import uuid4
from app.blob_storage import BlobStorageService
import json
from marshmallow import ValidationError
from app.schemas import PropertyCreateSchema, PropertyUpdateSchema

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

    # Validate required fields
    required_fields = ["price", "seller_id", "address", "specs"]
    for field in required_fields:
        if field not in data:
            errors.append(f"{field} is required")
            return errors

    # Validate price
    if not isinstance(data["price"], int) or data["price"] < 0:
        errors.append("Price must be a positive number")

    # Validate address
    if "address" in data:
        addr = data["address"]
        required_addr_fields = ["house_number", "street", "city", "postcode"]
        for field in required_addr_fields:
            if field not in addr:
                errors.append(f"Address {field} is required")

    # Validate specs
    if "specs" in data:
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
            "construction_year": int,
            "heating_type": str,
        }
        for field, field_type in required_details.items():
            if field not in details:
                errors.append(f"Detail {field} is required")
            elif not isinstance(details[field], field_type):
                errors.append(f"{field} must be a {field_type.__name__}")

    # Validate media if provided
    if "media" in data:
        if not isinstance(data["media"], list):
            errors.append("Media must be a list")
        else:
            for idx, media_item in enumerate(data["media"]):
                if "image_url" not in media_item:
                    errors.append(f"Media item {idx} missing image_url")

    # Validate status if provided
    if "status" in data and data["status"] not in Property.VALID_STATUSES:
        errors.append(
            f"Status must be one of: {', '.join(Property.VALID_STATUSES)}"
        )

    return errors


@bp.route("", methods=["GET"])
def get_properties():
    """List view - returns basic property info."""
    try:
        query = select(Property).options(
            joinedload(Property.address), joinedload(Property.specs)
        )

        # By default only show 'for_sale' properties unless include_all is True
        include_all = (
            request.args.get("include_all", "false").lower() == "true"
        )
        if not include_all:
            query = query.where(Property.status == "for_sale")

        # Add other filters if provided
        if request.args.get("min_price"):
            query = query.where(
                Property.price >= int(request.args.get("min_price"))
            )
        if request.args.get("max_price"):
            query = query.where(
                Property.price <= int(request.args.get("max_price"))
            )
        if request.args.get("bedrooms"):
            query = query.where(
                Property.bedrooms == int(request.args.get("bedrooms"))
            )
        if request.args.get("property_type"):
            query = query.join(PropertySpecs).where(
                PropertySpecs.property_type
                == request.args.get("property_type")
            )
        # Add explicit status filter if provided
        if request.args.get("status"):
            query = query.where(Property.status == request.args.get("status"))

        query = query.order_by(Property.price.desc())
        properties = list(db.session.execute(query).unique().scalars())

        return jsonify(
            [
                {
                    "property_id": str(p.id),
                    "price": p.price,
                    "bedrooms": p.bedrooms,
                    "bathrooms": p.bathrooms,
                    "main_image_url": p.main_image_url,
                    "created_at": p.created_at.isoformat(),
                    "seller_id": str(p.user_id),
                    "status": p.status,
                    "address": {
                        "house_number": (
                            p.address.house_number if p.address else None
                        ),
                        "street": p.address.street if p.address else None,
                        "city": p.address.city if p.address else None,
                        "postcode": p.address.postcode if p.address else None,
                    },
                    "specs": {
                        "property_type": (
                            p.specs.property_type if p.specs else None
                        ),
                        "square_footage": (
                            p.specs.square_footage if p.specs else None
                        ),
                    },
                }
                for p in properties
            ]
        )

    except Exception as e:
        current_app.logger.error(f"Error in get_properties: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/<uuid:property_id>", methods=["GET"])
def get_property(property_id):
    """Get a specific property."""
    try:
        property_item = db.session.get(Property, property_id)
        if property_item is None:
            return jsonify({"error": "Property not found"}), 404

        return jsonify(
            {
                "property_id": str(property_item.id),
                "price": property_item.price,
                "bedrooms": property_item.bedrooms,
                "bathrooms": property_item.bathrooms,
                "main_image_url": property_item.main_image_url,
                "created_at": property_item.created_at.isoformat(),
                "details": {
                    "description": (
                        property_item.details.description
                        if property_item.details
                        else None
                    ),
                    "construction_year": (
                        property_item.details.construction_year
                        if property_item.details
                        else None
                    ),
                    "heating_type": (
                        property_item.details.heating_type
                        if property_item.details
                        else None
                    ),
                },
                "features": {
                    "has_garden": (
                        property_item.features.has_garden
                        if property_item.features
                        else False
                    ),
                    "garden_size": (
                        property_item.features.garden_size
                        if property_item.features
                        else None
                    ),
                    "parking_spaces": (
                        property_item.features.parking_spaces
                        if property_item.features
                        else 0
                    ),
                    "has_garage": (
                        property_item.features.has_garage
                        if property_item.features
                        else False
                    ),
                },
                "image_urls": [
                    media.image_url
                    for media in property_item.media
                    if media.image_type != "floorplan"
                ],
                "floorplan_url": next(
                    (
                        media.image_url
                        for media in property_item.media
                        if media.image_type == "floorplan"
                    ),
                    None,
                ),
                "seller_id": str(property_item.user_id),
                "address": {
                    "house_number": (
                        property_item.address.house_number
                        if property_item.address
                        else None
                    ),
                    "street": (
                        property_item.address.street
                        if property_item.address
                        else None
                    ),
                    "city": (
                        property_item.address.city
                        if property_item.address
                        else None
                    ),
                    "postcode": (
                        property_item.address.postcode
                        if property_item.address
                        else None
                    ),
                    "latitude": (
                        property_item.address.latitude
                        if property_item.address
                        else None
                    ),
                    "longitude": (
                        property_item.address.longitude
                        if property_item.address
                        else None
                    ),
                },
                "specs": {
                    "bedrooms": (
                        property_item.specs.bedrooms
                        if property_item.specs
                        else None
                    ),
                    "bathrooms": (
                        property_item.specs.bathrooms
                        if property_item.specs
                        else None
                    ),
                    "property_type": (
                        property_item.specs.property_type
                        if property_item.specs
                        else None
                    ),
                    "square_footage": (
                        property_item.specs.square_footage
                        if property_item.specs
                        else None
                    ),
                    "reception_rooms": (
                        property_item.specs.reception_rooms
                        if property_item.specs
                        else None
                    ),
                    "epc_rating": (
                        property_item.specs.epc_rating
                        if property_item.specs
                        else None
                    ),
                },
                "last_updated": property_item.last_updated.isoformat(),
            }
        )

    except Exception as e:
        current_app.logger.error(f"Error getting property: {str(e)}")
        return jsonify({"error": str(e)}), 500


def preprocess_property_data(data):
    """Convert string numbers to proper types"""
    if "specs" in data:
        specs = data["specs"]
        if "square_footage" in specs:
            try:
                specs["square_footage"] = float(specs["square_footage"])
            except (ValueError, TypeError):
                pass  # Let schema validation handle invalid values
        if "bedrooms" in specs:
            try:
                specs["bedrooms"] = int(specs["bedrooms"])
            except (ValueError, TypeError):
                pass
        if "bathrooms" in specs:
            try:
                specs["bathrooms"] = int(specs["bathrooms"])
            except (ValueError, TypeError):
                pass
    return data


@bp.route("", methods=["POST"])
def create_property():
    """Create a new property listing."""
    try:
        data = preprocess_property_data(request.get_json())
        schema = PropertyCreateSchema()
        try:
            # Validate the data using schema
            validated_data = schema.load(data)
            # Use the validated data instead of raw data
            data = validated_data
        except ValidationError as err:
            return (
                jsonify(
                    {"error": "Validation failed", "details": err.messages}
                ),
                400,
            )

        warnings = []
        image_urls = []

        # Handle multipart form data with images
        if request.content_type and request.content_type.startswith(
            "multipart/form-data"
        ):
            # ... existing image handling code ...

            try:
                data = json.loads(request.form.get("data", "{}"))
            except json.JSONDecodeError:
                return (
                    jsonify(
                        {"error": "Invalid JSON data in form field 'data'"}
                    ),
                    400,
                )
        else:
            # Handle pure JSON request
            data = request.get_json()

        # Validate data
        errors = validate_property_data(data)
        if errors:
            return jsonify({"errors": errors}), 400

        property_id = uuid4()

        # Create property with main image and default status
        property = Property(
            id=property_id,
            price=int(data["price"]),
            bedrooms=int(data["specs"]["bedrooms"]),
            bathrooms=float(data["specs"]["bathrooms"]),
            main_image_url=image_urls[0] if image_urls else None,
            user_id=data["seller_id"],
            created_at=datetime.now(UTC),
            status=data.get("status", "for_sale"),
        )
        db.session.add(property)

        # Create media entries for all images
        for idx, image_url in enumerate(image_urls):
            media = PropertyMedia(
                property_id=property_id,
                image_url=image_url,
                image_type="main" if idx == 0 else "interior",
                display_order=idx,
            )
            db.session.add(media)

        # Create address
        address = Address(
            property_id=property_id,
            house_number=data["address"]["house_number"],
            street=data["address"]["street"],
            city=data["address"]["city"],
            postcode=data["address"]["postcode"],
        )

        try:
            lat, lon = geocode_address(address)
            address.latitude = lat
            address.longitude = lon
        except GeocodeError:
            warnings.append("Could not geocode address")

        db.session.add(address)

        # Create specs
        specs = PropertySpecs(
            property_id=property_id,
            bedrooms=data["specs"]["bedrooms"],
            bathrooms=data["specs"]["bathrooms"],
            reception_rooms=data["specs"]["reception_rooms"],
            square_footage=data["specs"]["square_footage"],
            property_type=data["specs"]["property_type"],
            epc_rating=data["specs"]["epc_rating"],
        )
        db.session.add(specs)

        # Create details if provided
        if "details" in data:
            from app.models import PropertyDetail

            details = PropertyDetail(
                property_id=property_id,
                description=data["details"]["description"],
                construction_year=data["details"]["construction_year"],
                heating_type=data["details"]["heating_type"],
            )
            db.session.add(details)

        # Create features if provided
        if "features" in data:
            from app.models import PropertyFeatures

            features = PropertyFeatures(
                property_id=property_id,
                has_garden=data["features"].get("has_garden", False),
                garden_size=data["features"].get("garden_size"),
                has_garage=data["features"].get("has_garage", False),
                parking_spaces=data["features"].get("parking_spaces", 0),
            )
            db.session.add(features)

        db.session.commit()
        return (
            jsonify(
                {
                    "property_id": str(property_id),
                    "message": "Property created successfully",
                    "warnings": warnings,
                    "image_urls": image_urls,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating property: {str(e)}")
        return (
            jsonify({"error": "Failed to create property", "details": str(e)}),
            500,
        )


def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@bp.route("/<uuid:property_id>", methods=["PUT"])
def update_property(property_id):
    """Update a property."""
    try:
        property_item = db.session.get(Property, property_id)
        if property_item is None:
            return jsonify({"error": "Property not found"}), 404

        # Load and validate data
        try:
            schema = PropertyUpdateSchema()
            validated_data = schema.load(request.get_json())
        except ValidationError as err:
            current_app.logger.error(f"Validation error: {err.messages}")
            return (
                jsonify(
                    {"error": "Validation failed", "details": err.messages}
                ),
                400,
            )

        # Check status transition if status is being updated
        if "status" in validated_data:
            current_status = property_item.status
            new_status = validated_data["status"]

            # Define valid transitions
            valid_transitions = {
                "for_sale": ["under_offer", "sold"],
                "under_offer": ["for_sale", "sold"],
                "sold": [],  # Can't transition from sold
            }

            if current_status == "sold":
                return (
                    jsonify(
                        {"error": "Cannot update status of sold property"}
                    ),
                    400,
                )

            if new_status not in valid_transitions[current_status]:
                return (
                    jsonify(
                        {
                            "error": (
                                "Invalid status transition from",
                                f"{current_status} to {new_status}",
                            )
                        }
                    ),
                    400,
                )

        # Update main property fields
        if "price" in validated_data:
            property_item.price = validated_data["price"]
        if "status" in validated_data:
            property_item.status = validated_data["status"]

        # Update specs if provided
        if "specs" in validated_data and property_item.specs:
            for key, value in validated_data["specs"].items():
                setattr(property_item.specs, key, value)

        db.session.commit()
        return jsonify(
            {
                "message": "Property updated successfully",
                "status": property_item.status,
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating property: {str(e)}")
        return jsonify({"error": "Failed to update property"}), 500


@bp.route("/<uuid:property_id>", methods=["DELETE"])
def delete_property(property_id):
    """Delete a property."""
    try:
        property_item = db.session.get(Property, property_id)
        if property_item is None:
            return jsonify({"error": "Property not found"}), 404

        # Delete images from blob storage
        blob_service = BlobStorageService()
        for media in property_item.media:
            try:
                blob_service.delete_image(media.image_url)
            except Exception as e:
                current_app.logger.error(f"Failed to delete image: {str(e)}")

        db.session.delete(property_item)
        db.session.commit()
        return jsonify({"message": "Property deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/user/<uuid:user_id>", methods=["GET"])
def get_user_properties(user_id):
    """Get all properties for a specific user."""
    try:
        query = (
            select(Property)
            .options(joinedload(Property.address), joinedload(Property.specs))
            .where(Property.user_id == user_id)
            .order_by(Property.price.desc())
        )

        properties = list(db.session.execute(query).unique().scalars())

        return jsonify(
            [
                {
                    "property_id": str(p.id),
                    "price": p.price,
                    "bedrooms": p.bedrooms,
                    "bathrooms": p.bathrooms,
                    "main_image_url": p.main_image_url,
                    "created_at": p.created_at.isoformat(),
                    "seller_id": str(p.user_id),
                    "address": {
                        "house_number": (
                            p.address.house_number if p.address else None
                        ),
                        "street": p.address.street if p.address else None,
                        "city": p.address.city if p.address else None,
                        "postcode": p.address.postcode if p.address else None,
                    },
                    "specs": {
                        "property_type": (
                            p.specs.property_type if p.specs else None
                        ),
                        "square_footage": (
                            p.specs.square_footage if p.specs else None
                        ),
                    },
                }
                for p in properties
            ]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/test-upload", methods=["POST"])
def test_upload():
    """Test endpoint for image upload"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            blob_service = BlobStorageService()
            image_url = blob_service.upload_image(
                file.read(), file.content_type
            )
            return jsonify({"message": "Upload successful", "url": image_url})

    except Exception as e:
        current_app.logger.error(f"Upload test error: {str(e)}")
        return jsonify({"error": str(e)}), 500
