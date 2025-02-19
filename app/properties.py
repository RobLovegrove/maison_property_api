from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    PropertyFeatures,
    PropertyMedia,
    PropertyDetail,
)
from datetime import datetime, UTC
from sqlalchemy.sql import select
from sqlalchemy.orm import joinedload

bp = Blueprint("properties", __name__)


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

        return jsonify(
            [
                {
                    "id": p.id,
                    "price": p.price,
                    "bedrooms": p.specs.bedrooms if p.specs else None,
                    "bathrooms": p.specs.bathrooms if p.specs else None,
                    "main_image_url": p.main_image_url,
                    "created_at": (
                        p.created_at.isoformat() if p.created_at else None
                    ),
                    "address": (
                        {
                            "street": p.address.street,
                            "city": p.address.city,
                            "postcode": p.address.postcode,
                        }
                        if p.address
                        else None
                    ),
                    "specs": (
                        {
                            "property_type": p.specs.property_type,
                            "square_footage": p.specs.square_footage,
                        }
                        if p.specs
                        else None
                    ),
                }
                for p in properties
            ]
        )

    except Exception as e:
        current_app.logger.error(f"Error in get_properties: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/<int:property_id>", methods=["GET"])
def get_property(property_id):
    try:
        current_app.logger.info(f"Fetching property with ID: {property_id}")
        property_item = (
            db.session.execute(
                select(Property)
                .options(
                    joinedload(Property.address),
                    joinedload(Property.specs),
                    joinedload(Property.features),
                    joinedload(Property.details),
                    joinedload(Property.media),
                )
                .filter(Property.id == property_id)
            )
            .unique()
            .scalar_one_or_none()
        )

        if property_item is None:
            return jsonify({"error": "Property not found"}), 404

        # Get additional images ordered by display_order
        try:
            additional_images = (
                [
                    media.image_url
                    for media in sorted(
                        [
                            m
                            for m in property_item.media
                            if m.image_type == "additional"
                        ],
                        key=lambda m: (
                            m.display_order is None,
                            m.display_order,
                        ),
                    )
                ]
                if property_item.media
                else []
            )
        except Exception as img_error:
            current_app.logger.error(
                f"Error processing additional images: {str(img_error)}"
            )
            additional_images = []

        # Get floorplan
        try:
            floorplan = (
                next(
                    (
                        media.image_url
                        for media in property_item.media
                        if media.image_type == "floorplan"
                    ),
                    None,
                )
                if property_item.media
                else None
            )
        except Exception as floor_error:
            current_app.logger.error(
                f"Error processing floorplan: {str(floor_error)}"
            )
            floorplan = None

        response = {
            "id": property_item.id,
            "price": property_item.price,
            "created_at": (
                property_item.created_at.isoformat()
                if property_item.created_at
                else None
            ),
            "address": (
                {
                    "house_number": property_item.address.house_number,
                    "street": property_item.address.street,
                    "city": property_item.address.city,
                    "postcode": property_item.address.postcode,
                    "latitude": property_item.address.latitude,
                    "longitude": property_item.address.longitude,
                }
                if property_item.address
                else None
            ),
            "specs": (
                {
                    "bedrooms": property_item.specs.bedrooms,
                    "bathrooms": property_item.specs.bathrooms,
                    "reception_rooms": property_item.specs.reception_rooms,
                    "square_footage": property_item.specs.square_footage,
                    "property_type": property_item.specs.property_type,
                    "epc_rating": property_item.specs.epc_rating,
                }
                if property_item.specs
                else None
            ),
            "features": (
                {
                    "has_garden": property_item.features.has_garden,
                    "garden_size": property_item.features.garden_size,
                    "parking_spaces": property_item.features.parking_spaces,
                    "has_garage": property_item.features.has_garage,
                }
                if property_item.features
                else None
            ),
            "details": (
                {
                    "description": property_item.details.description,
                    "property_type": property_item.details.property_type,
                    "construction_year": (
                        property_item.details.construction_year
                    ),
                    "parking_spaces": property_item.details.parking_spaces,
                    "heating_type": property_item.details.heating_type,
                }
                if property_item.details
                else None
            ),
            "images": {
                "main": property_item.main_image_url,
                "additional": additional_images,
                "floorplan": floorplan,
            },
        }
        return jsonify(response)
    except Exception as e:
        current_app.logger.exception(f"Error in get_property: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("", methods=["POST"])
def create_property():
    data = request.get_json()

    # Validate input data
    errors = validate_property_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        # Create main property
        property = Property(
            price=data["price"],
            bedrooms=data["specs"]["bedrooms"],
            bathrooms=data["specs"]["bathrooms"],
            main_image_url=data.get("main_image_url"),
            created_at=datetime.now(UTC),
            last_updated=datetime.now(UTC),
        )
        db.session.add(property)

        # Create address
        address = Address(
            property=property,
            house_number=data["address"]["house_number"],
            street=data["address"]["street"],
            city=data["address"]["city"],
            postcode=data["address"]["postcode"],
        )
        db.session.add(address)

        # Create specs
        specs = PropertySpecs(
            property=property,
            bedrooms=data["specs"]["bedrooms"],
            bathrooms=data["specs"]["bathrooms"],
            reception_rooms=data["specs"]["reception_rooms"],
            square_footage=data["specs"]["square_footage"],
            property_type=data["specs"]["property_type"],
            epc_rating=data["specs"]["epc_rating"],
        )
        db.session.add(specs)

        # Create features
        if "features" in data:
            features = PropertyFeatures(
                property=property,
                has_garden=data["features"].get("has_garden", False),
                garden_size=data["features"].get("garden_size"),
                parking_spaces=data["features"].get("parking_spaces", 0),
                has_garage=data["features"].get("has_garage", False),
            )
            db.session.add(features)

        # Create details
        if "details" in data:
            details = PropertyDetail(
                property=property,
                description=data["details"]["description"],
                property_type=data["details"]["property_type"],
                construction_year=data["details"]["construction_year"],
                parking_spaces=data["details"]["parking_spaces"],
                heating_type=data["details"]["heating_type"],
            )
            db.session.add(details)

        # Create media entries if provided
        if "media" in data:
            for image_data in data["media"]:
                media = PropertyMedia(
                    property=property,
                    image_url=image_data["url"],
                    is_main_image=image_data.get("is_main_image", False),
                    image_type=image_data.get("type", "interior"),
                )
                db.session.add(media)

        db.session.commit()
        return jsonify({"id": property.id}), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating property: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:property_id>", methods=["PUT"])
def update_property(property_id):
    property_item = db.session.get(Property, property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404

    data = request.get_json()

    try:
        # Update main property
        if "price" in data:
            property_item.price = data["price"]
        if "description" in data:
            property_item.description = data["description"]

        # Update address
        if "address" in data:
            addr = data["address"]
            if property_item.address:
                for key, value in addr.items():
                    setattr(property_item.address, key, value)

        # Update specs
        if "specs" in data:
            specs = data["specs"]
            if property_item.specs:
                for key, value in specs.items():
                    setattr(property_item.specs, key, value)

        # Update features
        if "features" in data:
            features = data["features"]
            if property_item.features:
                for key, value in features.items():
                    setattr(property_item.features, key, value)

        db.session.commit()
        return jsonify({"message": "Property updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/<int:property_id>", methods=["DELETE"])
def delete_property(property_id):
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
