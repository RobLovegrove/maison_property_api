from flask import Flask, jsonify, request
from flask_cors import CORS
from app.models import db, Property
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://realestate-website.com",
            "http://localhost:3000"  # for local development
        ]
    }
})

# Create tables
with app.app_context():
    db.create_all()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/properties', methods=['GET'])
def get_properties():
    property_type = request.args.get('property_type')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    min_beds = request.args.get('min_beds', type=int)

    query = Property.query

    if property_type:
        query = query.filter(Property.property_type == property_type)
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)
    if min_beds:
        query = query.filter(Property.bedrooms >= min_beds)

    properties = query.all()
    
    # Return only basic property information for list view
    return jsonify([{
        'id': p.id,
        'price': p.price,
        'address': p.address,
        'bedrooms': p.bedrooms,
        'bathrooms': p.bathrooms,
        'reception_rooms': p.reception_rooms,
        'square_footage': p.square_footage,
        'property_type': p.property_type,
        'epc_rating': p.epc_rating,
        'main_image_url': p.main_image_url
    } for p in properties])

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    property_item = Property.query.get(property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404
    
    # Return detailed property information for single property view
    response = {
        "id": property_item.id,
        "basic_info": {
            "price": property_item.price,
            "address": property_item.address,
            "property_type": property_item.property_type,
            "bedrooms": property_item.bedrooms,
            "bathrooms": property_item.bathrooms,
            "reception_rooms": property_item.reception_rooms,
            "square_footage": property_item.square_footage,
            "epc_rating": property_item.epc_rating
        },
        "description": property_item.description,
        "images": {
            "main_image": property_item.main_image_url,
            "additional_images": property_item.additional_image_urls,
            "floorplan": property_item.floorplan_url
        },
        "property_details": {
            "ownership_type": property_item.ownership_type,
            "leasehold_years_remaining": property_item.leasehold_years_remaining,
            "property_age": property_item.property_age,
            "council_tax_band": property_item.council_tax_band
        },
        "key_features": property_item.key_features
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 