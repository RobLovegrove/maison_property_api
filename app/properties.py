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
    required_fields = ["price", "user_id", "address", "specs"]
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

    # Validate media if provided
    if "media" in data:
        if not isinstance(data["media"], list):
            errors.append("Media must be a list")
        else:
            for idx, media_item in enumerate(data["media"]):
                if "image_url" not in media_item:
                    errors.append(f"Media item {idx} missing image_url")

    return errors


@bp.route("", methods=["GET"])
def get_properties():
    """List view - returns basic property info."""
    try:
        query = select(Property).options(
            joinedload(Property.address), joinedload(Property.specs)
        )

        # Add filters if provided
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

        query = query.order_by(Property.price.desc())
        properties = list(db.session.execute(query).unique().scalars())

        return jsonify(
            [
                {
                    "id": str(p.id),
                    "price": p.price,
                    "bedrooms": p.bedrooms,
                    "bathrooms": p.bathrooms,
                    "main_image_url": p.main_image_url,
                    "created_at": p.created_at.isoformat(),
                    "owner_id": p.user_id,
                    "address": {
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
    """Get a single property by ID."""
    try:
        result = db.session.get(
            Property,
            property_id,
            options=[
                joinedload(Property.address),
                joinedload(Property.specs),
                joinedload(Property.media),
                joinedload(Property.details),
                joinedload(Property.features),
            ],
        )

        if result is None:
            return jsonify({"error": "Property not found"}), 404

        image_urls = [
            media.image_url
            for media in result.media
            if media.image_type != "floorplan"
        ]

        floorplan_url = next(
            (
                media.image_url
                for media in result.media
                if media.image_type == "floorplan"
            ),
            None,
        )

        return (
            jsonify(
                {
                    "id": str(result.id),
                    "price": result.price,
                    "bedrooms": result.bedrooms,
                    "bathrooms": result.bathrooms,
                    "main_image_url": result.main_image_url,
                    "image_urls": image_urls,
                    "floorplan_url": floorplan_url,
                    "created_at": result.created_at.isoformat(),
                    "owner_id": result.user_id,
                    "address": {
                        "street": (
                            result.address.street if result.address else None
                        ),
                        "city": (
                            result.address.city if result.address else None
                        ),
                        "postcode": (
                            result.address.postcode if result.address else None
                        ),
                        "latitude": (
                            result.address.latitude if result.address else None
                        ),
                        "longitude": (
                            result.address.longitude
                            if result.address
                            else None
                        ),
                    },
                    "specs": (
                        {
                            "bedrooms": (
                                result.specs.bedrooms if result.specs else None
                            ),
                            "bathrooms": (
                                result.specs.bathrooms
                                if result.specs
                                else None
                            ),
                            "property_type": (
                                result.specs.property_type
                                if result.specs
                                else None
                            ),
                            "square_footage": (
                                result.specs.square_footage
                                if result.specs
                                else None
                            ),
                            "reception_rooms": (
                                result.specs.reception_rooms
                                if result.specs
                                else None
                            ),
                            "epc_rating": (
                                result.specs.epc_rating
                                if result.specs
                                else None
                            ),
                        }
                        if result.specs
                        else None
                    ),
                    "details": {
                        "description": (
                            result.details.description
                            if result.details
                            else None
                        ),
                        "construction_year": (
                            result.details.construction_year
                            if result.details
                            else None
                        ),
                        "heating_type": (
                            result.details.heating_type
                            if result.details
                            else None
                        ),
                        "parking_spaces": (
                            result.details.parking_spaces
                            if result.details
                            else None
                        ),
                    },
                    "features": {
                        "has_garden": (
                            result.features.has_garden
                            if result.features
                            else False
                        ),
                        "garden_size": (
                            result.features.garden_size
                            if result.features
                            else None
                        ),
                        "has_garage": (
                            result.features.has_garage
                            if result.features
                            else False
                        ),
                        "parking_spaces": (
                            result.features.parking_spaces
                            if result.features
                            else 0
                        ),
                    },
                    "last_updated": result.last_updated.isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error getting property: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("", methods=["POST"])
def create_property():
    """Create a new property."""
    try:
        # Initialize blob storage service
        blob_service = BlobStorageService()

        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            files = None
        else:
            data = request.form.to_dict()
            files = request.files
            # Parse nested JSON strings from form data
            if "specs" in data:
                data["specs"] = json.loads(data["specs"])
            if "address" in data:
                data["address"] = json.loads(data["address"])
            if "features" in data:
                data["features"] = json.loads(data["features"])
            if "details" in data:
                data["details"] = json.loads(data["details"])

        # Validate data
        errors = validate_property_data(data)
        if errors:
            return jsonify({"errors": errors}), 400

        property_id = uuid4()
        warnings = []
        image_urls = []

        # Handle image uploads if files exist
        if files and "images" in files:
            for image in files.getlist("images"):
                if image and allowed_file(image.filename):
                    try:
                        # Upload to blob storage
                        image_url = blob_service.upload_image(
                            image.read(), image.content_type
                        )
                        image_urls.append(image_url)
                    except Exception as e:
                        warnings.append(f"Failed to upload image: {str(e)}")

        # Create property with first image as main image
        property = Property(
            id=property_id,
            price=int(data["price"]),
            bedrooms=int(data["specs"]["bedrooms"]),
            bathrooms=float(data["specs"]["bathrooms"]),
            main_image_url=image_urls[0] if image_urls else None,
            user_id=int(data["user_id"]),
            created_at=datetime.now(UTC),
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
                property_type=data["details"]["property_type"],
                construction_year=data["details"]["construction_year"],
                parking_spaces=data["details"]["parking_spaces"],
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
                    "id": str(property_id),
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
        return jsonify({"error": str(e)}), 500


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

        data = request.get_json()

        # Update main property fields
        for key, value in data.items():
            if key not in ("address", "specs", "features", "details", "media"):
                setattr(property_item, key, value)

        # Update related objects
        if "address" in data and property_item.address:
            for key, value in data["address"].items():
                setattr(property_item.address, key, value)

        if "specs" in data and property_item.specs:
            for key, value in data["specs"].items():
                setattr(property_item.specs, key, value)

        db.session.commit()
        return jsonify({"message": "Property updated successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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


@bp.route("/user/<int:user_id>", methods=["GET"])
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

        return (
            jsonify(
                [
                    {
                        "id": str(p.id),
                        "price": p.price,
                        "bedrooms": p.bedrooms,
                        "bathrooms": p.bathrooms,
                        "main_image_url": p.main_image_url,
                        "created_at": p.created_at.isoformat(),
                        "owner_id": p.user_id,
                        "address": {
                            "street": p.address.street if p.address else None,
                            "city": p.address.city if p.address else None,
                            "postcode": (
                                p.address.postcode if p.address else None
                            ),
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
            ),
            200,
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
