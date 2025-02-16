from flask import (
    Blueprint,
    jsonify,
    request,
    render_template_string,
)
from app import db
from app.models import (
    Property,
    Address,
    PropertySpecs,
    PropertyFeatures,
    PropertyMedia,
)
import os
import markdown2

bp = Blueprint("main", __name__)


def validate_property_data(data):
    """Validate property data from request"""
    errors = []

    # Validate main property data
    if "price" not in data or not isinstance(data["price"], int):
        errors.append("Price must be a number")
    if "description" not in data or not isinstance(data["description"], str):
        errors.append("Description is required")

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

    return errors


@bp.route("/", methods=["GET"])
def index():
    """Return README.md content as HTML"""
    # Get the project root directory
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Read README.md
    with open(os.path.join(root_dir, "README.md"), "r") as f:
        content = f.read()

    # Convert markdown to HTML with extras
    html = markdown2.markdown(
        content,
        extras=[
            "fenced-code-blocks",
            "code-friendly",
            "tables",
            "header-ids",
            "break-on-newline",
        ],
    )

    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MaiSON Property API</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/\
github-markdown.min.css"
        >
        <link
            rel="stylesheet"
            href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/\
github.min.css"
        >
        <script
            src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/\
highlight.min.js"
        ></script>
        <script>hljs.highlightAll();</script>
        <style>
            .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }
            @media (max-width: 767px) {
                .markdown-body {
                    padding: 15px;
                }
            }
            /* Make code text white for better readability */
            code {
                color: #ffffff !important;
            }
        </style>
    </head>
    <body class="markdown-body">
        {{ content|safe }}
    </body>
    </html>
    """

    return render_template_string(template, content=html)


@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"})


@bp.route("/api/properties", methods=["GET"])
def get_properties():
    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Limit per_page to prevent excessive requests
    per_page = min(per_page, 50)

    # Filters
    min_price = request.args.get("min_price", type=int)
    max_price = request.args.get("max_price", type=int)
    bedrooms = request.args.get("bedrooms", type=int)
    property_type = request.args.get("property_type")
    city = request.args.get("city")
    min_square_footage = request.args.get("min_square_footage", type=float)
    bathrooms = request.args.get("bathrooms", type=int)
    reception_rooms = request.args.get("reception_rooms", type=int)
    has_garden = request.args.get("has_garden", type=bool)
    has_garage = request.args.get("has_garage", type=bool)
    epc_rating = request.args.get("epc_rating")
    ownership_type = request.args.get("ownership_type")
    postcode_area = request.args.get("postcode_area")

    # Build query with explicit ordering
    query = (
        Property.query.join(PropertySpecs)
        .join(Address)
        .join(PropertyFeatures)
        .order_by(Property.created_at.desc(), Property.id.desc())
    )

    # Debug query
    print("\nSQL Query:")
    print(query.statement.compile(compile_kwargs={"literal_binds": True}))

    # Apply filters
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)
    if bedrooms:
        query = query.filter(PropertySpecs.bedrooms >= bedrooms)
    if property_type:
        query = query.filter(PropertySpecs.property_type == property_type)
    if city:
        query = query.filter(Address.city.ilike(f"%{city}%"))
    if min_square_footage:
        query = query.filter(
            PropertySpecs.square_footage >= min_square_footage
        )
    if bathrooms:
        query = query.filter(PropertySpecs.bathrooms >= bathrooms)
    if reception_rooms:
        query = query.filter(PropertySpecs.reception_rooms >= reception_rooms)
    if has_garden is not None:
        query = query.filter(PropertyFeatures.has_garden == has_garden)
    if has_garage is not None:
        query = query.filter(PropertyFeatures.has_garage == has_garage)
    if epc_rating:
        query = query.filter(PropertySpecs.epc_rating == epc_rating)
    if ownership_type:
        query = query.filter(Property.ownership_type == ownership_type)
    if postcode_area:
        query = query.filter(Address.postcode.ilike(f"{postcode_area}%"))

    # Paginate results
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        {
            "properties": [
                {
                    "id": p.id,
                    "price": p.price,
                    "status": p.status,
                    "created_at": p.created_at.isoformat(),
                    "address": {
                        "house_number": p.address.house_number,
                        "street": p.address.street,
                        "city": p.address.city,
                        "postcode": p.address.postcode,
                    },
                    "specs": {
                        "bedrooms": p.specs.bedrooms,
                        "bathrooms": p.specs.bathrooms,
                        "property_type": p.specs.property_type,
                        "square_footage": p.specs.square_footage,
                    },
                    "features": {
                        "has_garden": (
                            p.features.has_garden if p.features else False
                        ),
                        "parking_spaces": (
                            p.features.parking_spaces if p.features else 0
                        ),
                    },
                    "main_image": p.main_image_url,
                }
                for p in paginated.items
            ],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            },
        }
    )


@bp.route("/api/properties/<int:property_id>", methods=["GET"])
def get_property(property_id):
    property_item = Property.query.get(property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404

    response = {
        "id": property_item.id,
        "price": property_item.price,
        "status": property_item.status,
        "description": property_item.description,
        "address": {
            "house_number": property_item.address.house_number,
            "street": property_item.address.street,
            "city": property_item.address.city,
            "postcode": property_item.address.postcode,
        },
        "specs": {
            "bedrooms": property_item.specs.bedrooms,
            "bathrooms": property_item.specs.bathrooms,
            "reception_rooms": property_item.specs.reception_rooms,
            "square_footage": property_item.specs.square_footage,
            "property_type": property_item.specs.property_type,
            "epc_rating": property_item.specs.epc_rating,
        },
        "features": {
            "has_garden": property_item.features.has_garden,
            "garden_size": property_item.features.garden_size,
            "parking_spaces": property_item.features.parking_spaces,
            "has_garage": property_item.features.has_garage,
        },
        "images": {
            "main": property_item.main_image_url,
            "additional": property_item.additional_image_urls or [],
            "floorplan": property_item.floorplan_url,
        },
    }
    return jsonify(response)


@bp.route("/api/properties", methods=["POST"])
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
            status="for_sale",
            description=data["description"],
            ownership_type=data.get("ownership_type", "freehold"),
            key_features=data.get("key_features", []),
            council_tax_band=data.get("council_tax_band", "Unknown"),
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

        # Create features if provided
        if "features" in data:
            features = PropertyFeatures(
                property=property,
                has_garden=data["features"].get("has_garden", False),
                garden_size=data["features"].get("garden_size"),
                parking_spaces=data["features"].get("parking_spaces", 0),
                has_garage=data["features"].get("has_garage", False),
            )
            db.session.add(features)

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
        return jsonify({"error": str(e)}), 500


@bp.route("/api/properties/<int:property_id>", methods=["PUT"])
def update_property(property_id):
    property_item = Property.query.get(property_id)
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


@bp.route("/api/properties/<int:property_id>", methods=["DELETE"])
def delete_property(property_id):
    property_item = Property.query.get(property_id)
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
