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

    return jsonify(query.all())

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    property_item = Property.query.get(property_id)
    if property_item is None:
        return jsonify({"error": "Property not found"}), 404
    return jsonify(property_item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 