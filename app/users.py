from flask import Blueprint, jsonify, request, current_app
from app import db
from app.models import (
    User,
    Property,
    UserRole,
    SavedProperty,
    PropertyNegotiation,
    OfferTransaction,
)
from app.schemas import (
    UserSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserDashboardSchema,
)
from marshmallow import ValidationError
from datetime import datetime, timezone

bp = Blueprint("users", __name__)


@bp.route("", methods=["POST"])
def create_user():
    """Create a new user with roles using provided Firebase UUID."""
    try:
        schema = UserCreateSchema()
        data = schema.load(request.get_json())

        # Check if email already exists
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already registered"}), 400

        # Check if user_id was provided
        if "user_id" not in data:
            return jsonify({"error": "user_id is required"}), 400

        # Create user with provided UUID
        user = User(
            id=data["user_id"],  # Use the Firebase UUID
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data.get("phone_number"),
        )

        # Add roles
        roles = data.get(
            "roles", [{"role_type": "buyer"}]
        )  # Default to buyer if no roles specified
        for role in roles:
            user_role = UserRole(role_type=role["role_type"])
            user.roles.append(user_role)

        db.session.add(user)
        db.session.commit()

        # Use UserSchema to serialize the response
        response_schema = UserSchema()
        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "user": response_schema.dump(user),
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Failed to create user"}), 500


@bp.route("/<uuid:user_id>", methods=["GET"])
def get_user(user_id):
    """Get basic user details"""
    user = User.query.get_or_404(user_id)

    schema = UserSchema(
        only=(
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "full_name",
            "roles",
        )
    )

    return jsonify(schema.dump(user))


@bp.route("/<uuid:user_id>", methods=["PUT"])
def update_user(user_id):
    """Update user details."""
    try:
        user = User.query.get_or_404(user_id)
        schema = UserUpdateSchema()
        data = schema.load(request.get_json(), partial=True)

        # Check email uniqueness if being updated
        if "email" in data and data["email"] != user.email:
            if User.query.filter_by(email=data["email"]).first():
                return jsonify({"error": "Email already registered"}), 400

        for key, value in data.items():
            setattr(user, key, value)

        db.session.commit()
        return jsonify(
            {"message": "User updated successfully", "user": schema.dump(user)}
        )

    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bp.route("/<uuid:user_id>/dashboard", methods=["GET"])
def get_user_dashboard(user_id):
    """Get a user's dashboard data including their properties,
    offers, and saved listings"""

    # Get the user and verify they exist
    user = User.query.get_or_404(user_id)

    # Build dashboard data
    dashboard_data = {
        "user": user,
        "roles": user.roles,
        "listed_properties": [],
        "saved_properties": [],
        "negotiations_as_buyer": [],
        "negotiations_as_seller": [],
    }

    # If user is a seller, get their listed properties and negotiations
    if any(role.role_type == "seller" for role in user.roles):
        # Get properties with related data
        properties = (
            Property.query.filter_by(seller_id=user_id)
            .options(
                db.joinedload(Property.address), db.joinedload(Property.specs)
            )
            .all()
        )
        dashboard_data["listed_properties"] = properties

        # Get all active negotiations for their properties
        for property in properties:
            negotiations = (
                PropertyNegotiation.query.filter_by(property_id=property.id)
                .options(
                    db.joinedload(PropertyNegotiation.transactions),
                    db.joinedload(PropertyNegotiation.buyer),
                )
                .all()
            )
            dashboard_data["negotiations_as_seller"].extend(negotiations)

    # If user is a buyer, get their saved properties and negotiations
    if any(role.role_type == "buyer" for role in user.roles):
        # Get saved properties with notes
        saved = SavedProperty.query.filter_by(user_id=user_id).all()
        saved_properties = []
        for save in saved:
            property = (
                Property.query.filter_by(id=save.property_id)
                .options(
                    db.joinedload(Property.address),
                    db.joinedload(Property.specs),
                )
                .first()
            )
            if property:
                # Create property dict with saved notes
                property_dict = {
                    "property_id": str(property.id),
                    "price": property.price,
                    "status": property.status,
                    "main_image_url": property.main_image_url,
                    "notes": save.notes,
                    "saved_at": save.created_at,
                    "address": {
                        "street": (
                            property.address.street
                            if property.address
                            else None
                        ),
                        "city": (
                            property.address.city if property.address else None
                        ),
                        "postcode": (
                            property.address.postcode
                            if property.address
                            else None
                        ),
                    },
                    "specs": {
                        "bedrooms": (
                            property.specs.bedrooms if property.specs else None
                        ),
                        "bathrooms": (
                            property.specs.bathrooms
                            if property.specs
                            else None
                        ),
                        "property_type": (
                            property.specs.property_type
                            if property.specs
                            else None
                        ),
                    },
                }
                saved_properties.append(property_dict)
        dashboard_data["saved_properties"] = saved_properties

        # Get all negotiations where they are the buyer
        negotiations = (
            PropertyNegotiation.query.filter_by(buyer_id=user_id)
            .options(
                db.joinedload(PropertyNegotiation.transactions),
                db.joinedload(PropertyNegotiation.property),
            )
            .all()
        )
        dashboard_data["negotiations_as_buyer"] = negotiations

    # Serialize and return the data
    schema = UserDashboardSchema()
    return jsonify(schema.dump(dashboard_data))


@bp.route("/<uuid:user_id>/saved-properties", methods=["POST"])
def save_property(user_id):
    """Save a property for a buyer"""
    try:
        # Verify user exists and is a buyer
        user = User.query.get_or_404(user_id)
        if not any(role.role_type == "buyer" for role in user.roles):
            return (
                jsonify({"error": "User must be a buyer to save properties"}),
                403,
            )

        data = request.get_json()

        # Validate required property_id in request
        if not data or "property_id" not in data:
            return jsonify({"error": "property_id is required"}), 400

        property_id = data["property_id"]

        # Verify property exists
        property = Property.query.get(property_id)
        if not property:
            return jsonify({"error": "Property not found"}), 404

        # Check if already saved
        existing_save = SavedProperty.query.filter_by(
            user_id=user_id, property_id=property_id
        ).first()

        if existing_save:
            return jsonify({"error": "Property already saved"}), 400

        # Create new saved property
        saved_property = SavedProperty(
            user_id=user_id,
            property_id=property_id,
            notes=data.get("notes", ""),  # Optional notes
        )

        db.session.add(saved_property)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Property saved successfully",
                    "saved_property": {
                        "user_id": str(user_id),
                        "property_id": str(property_id),
                        "notes": saved_property.notes,
                        "created_at": saved_property.created_at.isoformat(),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving property: {str(e)}")
        return jsonify({"error": "Failed to save property"}), 500


@bp.route(
    "/<uuid:user_id>/saved-properties/<uuid:property_id>", methods=["DELETE"]
)
def remove_saved_property(user_id, property_id):
    """Remove a saved property for a buyer"""
    try:
        # Verify user exists and is a buyer
        user = User.query.get_or_404(user_id)
        if not any(role.role_type == "buyer" for role in user.roles):
            return (
                jsonify(
                    {
                        "error": (
                            "User must be a buyer "
                            "to manage saved properties"
                        )
                    }
                ),
                403,
            )

        # Find the saved property
        saved_property = SavedProperty.query.filter_by(
            user_id=user_id, property_id=property_id
        ).first()

        if not saved_property:
            return (
                jsonify({"error": "Property not found in saved properties"}),
                404,
            )

        # Remove the saved property
        db.session.delete(saved_property)
        db.session.commit()

        return jsonify(
            {
                "message": "Property removed from saved properties",
                "removed_property": {
                    "user_id": str(user_id),
                    "property_id": str(property_id),
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing saved property: {str(e)}")
        return jsonify({"error": "Failed to remove saved property"}), 500


@bp.route(
    "/<uuid:user_id>/saved-properties/<uuid:property_id>/notes",
    methods=["PATCH"],
)
def update_saved_property_notes(user_id, property_id):
    """Update notes for a saved property"""
    try:
        # Verify user exists and is a buyer
        user = User.query.get_or_404(user_id)
        if not any(role.role_type == "buyer" for role in user.roles):
            return (
                jsonify(
                    {
                        "error": (
                            "User must be a buyer "
                            "to update saved properties"
                        )
                    }
                ),
                403,
            )

        # Find the saved property
        saved_property = SavedProperty.query.filter_by(
            user_id=user_id, property_id=property_id
        ).first()

        if not saved_property:
            return (
                jsonify({"error": "Property not found in saved properties"}),
                404,
            )

        # Get and validate the new notes
        data = request.get_json()
        if not data or "notes" not in data:
            return jsonify({"error": "notes field is required"}), 400

        # Update the notes
        saved_property.notes = data["notes"]
        db.session.commit()

        return jsonify(
            {
                "message": "Notes updated successfully",
                "saved_property": {
                    "user_id": str(user_id),
                    "property_id": str(property_id),
                    "notes": saved_property.notes,
                    "updated_at": (
                        saved_property.updated_at.isoformat()
                        if saved_property.updated_at
                        else None
                    ),
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"Error updating saved property notes: {str(e)}"
        )
        return jsonify({"error": "Failed to update notes"}), 500


@bp.route("", methods=["GET"])
def get_users():
    """Get all users with role counts"""
    try:
        # Get all users with seller role
        sellers = (
            db.session.query(User.id)
            .join(UserRole)
            .filter(UserRole.role_type == "seller")
            .all()
        )
        seller_ids = [str(seller[0]) for seller in sellers]

        # Get all users with buyer role
        buyers = (
            db.session.query(User.id)
            .join(UserRole)
            .filter(UserRole.role_type == "buyer")
            .all()
        )
        buyer_ids = [str(buyer[0]) for buyer in buyers]

        """ Calculate total unique users by combining
        both lists and getting unique count"""
        unique_users = set(seller_ids + buyer_ids)

        response = {
            "sellers": seller_ids,
            "buyers": buyer_ids,
            "counts": {
                "total_sellers": len(seller_ids),
                "total_buyers": len(buyer_ids),
                "total_unique_users": len(unique_users),
            },
        }

        return jsonify(response)

    except Exception as e:
        current_app.logger.error(f"Error fetching users: {str(e)}")
        return jsonify({"error": "Failed to fetch users"}), 500


@bp.route("/<uuid:user_id>/offers", methods=["POST"])
def create_offer(user_id):
    """Create or counter an offer on a property"""
    try:
        # Verify user exists
        user = User.query.get_or_404(user_id)

        data = request.get_json()

        # Validate required fields
        if not data or "property_id" not in data or "offer_amount" not in data:
            return (
                jsonify(
                    {"error": "property_id and offer_amount are required"}
                ),
                400,
            )

        property_id = data["property_id"]
        offer_amount = data["offer_amount"]

        # Verify property exists
        property = Property.query.get(property_id)
        if not property:
            return jsonify({"error": "Property not found"}), 404

        # Check if this is a counter-offer
        is_counter = data.get("negotiation_id") is not None

        if is_counter:
            # Handle counter-offer
            negotiation = PropertyNegotiation.query.get(data["negotiation_id"])
            if not negotiation:
                return jsonify({"error": "Negotiation not found"}), 404

            # Verify user is involved in this negotiation
            if str(user_id) != str(negotiation.buyer_id) and str(
                user_id
            ) != str(property.user_id):
                return (
                    jsonify({"error": "Unauthorized to make counter-offer"}),
                    403,
                )

            # Create new transaction in existing negotiation
            transaction = OfferTransaction(
                negotiation_id=negotiation.id,
                offer_amount=offer_amount,
                made_by=user_id,
            )
            negotiation.last_offer_by = user_id
            negotiation.status = "active"

            db.session.add(transaction)

        else:
            # Handle new offer
            # Verify user is a buyer
            if not any(role.role_type == "buyer" for role in user.roles):
                return (
                    jsonify({"error": "User must be a buyer to make offers"}),
                    403,
                )

            # Verify user isn't the seller
            if str(user_id) == str(property.user_id):
                return (
                    jsonify(
                        {"error": "Cannot make offer on your own property"}
                    ),
                    400,
                )

            # Check for existing active negotiation
            existing_negotiation = PropertyNegotiation.query.filter_by(
                property_id=property_id, buyer_id=user_id, status="active"
            ).first()

            if existing_negotiation:
                return (
                    jsonify({"error": "Active negotiation already exists"}),
                    400,
                )

            # Create new negotiation
            negotiation = PropertyNegotiation(
                property_id=property_id,
                buyer_id=user_id,
                status="active",
                last_offer_by=user_id,
            )
            db.session.add(negotiation)
            db.session.flush()  # Get negotiation ID

            # Create first transaction
            transaction = OfferTransaction(
                negotiation_id=negotiation.id,
                offer_amount=offer_amount,
                made_by=user_id,
            )
            db.session.add(transaction)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Offer submitted successfully",
                    "negotiation": {
                        "negotiation_id": str(negotiation.id),
                        "property_id": str(property_id),
                        "buyer_id": str(negotiation.buyer_id),
                        "current_offer": offer_amount,
                        "status": negotiation.status,
                        "created_at": negotiation.created_at.isoformat(),
                        "last_offer_by": str(negotiation.last_offer_by),
                        "awaiting_response_from": (
                            "seller"
                            if str(user_id) == str(negotiation.buyer_id)
                            else "buyer"
                        ),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating offer: {str(e)}")
        return jsonify({"error": "Failed to create offer"}), 500


@bp.route("/<uuid:user_id>/offers/<uuid:negotiation_id>", methods=["PUT"])
def update_offer_status(user_id, negotiation_id):
    """Update an offer's status (accept/reject/cancel)"""
    try:
        # Get the negotiation
        negotiation = PropertyNegotiation.query.get_or_404(negotiation_id)
        property_item = Property.query.get(negotiation.property_id)

        # Verify user is involved in this negotiation
        if str(user_id) != str(property_item.user_id) and str(user_id) != str(
            negotiation.buyer_id
        ):
            return (
                jsonify(
                    {
                        "error": (
                            "Only the buyer or seller "
                            "can update offer status"
                        )
                    }
                ),
                403,
            )

        data = request.get_json()
        if not data or "action" not in data:
            return jsonify({"error": "action field is required"}), 400

        action = data["action"]
        if action not in ["accept", "reject", "cancel"]:
            return (
                jsonify(
                    {"error": "action must be 'accept', 'reject', or 'cancel'"}
                ),
                400,
            )

        # Get the latest offer
        latest_offer = (
            OfferTransaction.query.filter_by(negotiation_id=negotiation_id)
            .order_by(OfferTransaction.created_at.desc())
            .first()
        )

        # Check if negotiation is already completed
        if negotiation.status in ["accepted", "rejected", "cancelled"]:
            return (
                jsonify(
                    {
                        "error": (
                            f"Cannot update: negotiation is already "
                            f"{negotiation.status}"
                        )
                    }
                ),
                400,
            )

        # Verify the right person is taking action based on last offer
        is_seller = str(user_id) == str(property_item.user_id)
        last_offer_by_seller = str(latest_offer.made_by) == str(
            property_item.user_id
        )

        if action in ["accept", "reject"]:
            # Can only accept/reject if the other party made the last offer
            if is_seller == last_offer_by_seller:
                action_type = (
                    "accept/reject" if action == "accept" else "reject"
                )
                by_role = "seller" if is_seller else "buyer"
                return (
                    jsonify(
                        {
                            "error": (
                                f"Cannot {action_type} your own offer. "
                                f"Waiting for {by_role} response"
                            )
                        }
                    ),
                    400,
                )

        # Handle different actions
        if action == "accept":
            negotiation.status = "accepted"
            property_item.status = "under_offer"

            # Record who accepted the offer
            negotiation.accepted_by = user_id
            negotiation.accepted_at = datetime.now(timezone.utc)

        elif action == "reject":
            negotiation.status = "rejected"
            negotiation.rejected_by = user_id
            negotiation.rejected_at = datetime.now(timezone.utc)

        else:  # cancel
            # Get all offers in chronological order
            all_offers = (
                OfferTransaction.query.filter_by(negotiation_id=negotiation_id)
                .order_by(OfferTransaction.created_at.asc())
                .all()
            )

            # Can only cancel your own most recent offer
            if not (is_seller == last_offer_by_seller):
                return (
                    jsonify(
                        {
                            "error": (
                                "Can only cancel your own most recent offer"
                            )
                        }
                    ),
                    400,
                )

            # Check if this is the first offer in the negotiation
            is_first_offer = latest_offer == all_offers[0]

            if is_first_offer and not is_seller:
                # If buyer cancels their first offer, cancel entire negotiation
                negotiation.status = "cancelled"
                negotiation.cancelled_at = datetime.now(timezone.utc)

                # If property was under offer due to this negotiation revert it
                if (
                    property_item.status == "under_offer"
                    and not PropertyNegotiation.query.filter(
                        PropertyNegotiation.property_id == property_item.id,
                        PropertyNegotiation.id != negotiation_id,
                        PropertyNegotiation.status == "accepted",
                    ).first()
                ):
                    property_item.status = "for_sale"
            else:
                """For all other cases (seller cancelling counter-offer
                or buyer cancelling counter-offer),
                revert to the previous offer from the other party"""
                previous_offers = [
                    o
                    for o in all_offers
                    if str(o.made_by)
                    == (
                        str(negotiation.buyer_id)
                        if is_seller
                        else str(property_item.user_id)
                    )
                ]

                if previous_offers:
                    # Set the last offer from the other party as current offer
                    last_other_offer = previous_offers[-1]
                    negotiation.last_offer_by = last_other_offer.made_by
                    negotiation.status = "active"
                else:
                    # This shouldn't happen, but handle it just in case
                    negotiation.status = "cancelled"
                    negotiation.cancelled_at = datetime.now(timezone.utc)

        db.session.commit()

        # Get the current active offer for the response
        current_offer = (
            OfferTransaction.query.filter_by(negotiation_id=negotiation_id)
            .order_by(OfferTransaction.created_at.desc())
            .first()
        )

        return jsonify(
            {
                "message": (
                    "Negotiation cancelled"
                    if negotiation.status == "cancelled"
                    else "Counter-offer cancelled, reverted to previous offer"
                ),
                "negotiation": {
                    "negotiation_id": str(negotiation.id),
                    "property_id": str(property_item.id),
                    "buyer_id": str(negotiation.buyer_id),
                    "seller_id": str(property_item.user_id),
                    "current_offer_amount": current_offer.offer_amount,
                    "status": negotiation.status,
                    "updated_at": negotiation.updated_at.isoformat(),
                    "action_by": str(user_id),
                    "property_status": property_item.status,
                    "last_offer_by": str(current_offer.made_by),
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating offer status: {str(e)}")
        return jsonify({"error": "Failed to update offer status"}), 500
