#!/usr/bin/env python3
"""
Script to check if there's any data in the Address and PropertySpecs tables.
"""

import sys
import logging
from app import db, create_app
from app.models import Property, Address, PropertySpecs
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data():
    """Check if there's any data in the Address and PropertySpecs tables."""
    app = create_app()
    with app.app_context():
        try:
            # Count records in each table
            property_count = Property.query.count()
            address_count = Address.query.count()
            specs_count = PropertySpecs.query.count()
            
            logger.info(f"Data counts:")
            logger.info(f"Properties: {property_count}")
            logger.info(f"Addresses: {address_count}")
            logger.info(f"PropertySpecs: {specs_count}")
            
            # Check if there's any data in the Address table
            if address_count > 0:
                # Get a sample address
                sample_address = Address.query.first()
                logger.info(f"Sample address (ID: {sample_address.id}):")
                logger.info(f"  property_id: {sample_address.property_id}")
                logger.info(f"  house_number: {sample_address.house_number}")
                logger.info(f"  street: {sample_address.street}")
                logger.info(f"  city: {sample_address.city}")
                logger.info(f"  postcode: {sample_address.postcode}")
            else:
                logger.warning("No data found in the Address table!")
                
                # Check if the table exists
                connection = db.engine.connect()
                result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'addresses')"))
                table_exists = result.scalar()
                logger.info(f"Address table exists: {table_exists}")
            
            # Check if there's any data in the PropertySpecs table
            if specs_count > 0:
                # Get a sample specs
                sample_specs = PropertySpecs.query.first()
                logger.info(f"Sample specs (ID: {sample_specs.id}):")
                logger.info(f"  property_id: {sample_specs.property_id}")
                logger.info(f"  property_type: {sample_specs.property_type}")
                logger.info(f"  square_footage: {sample_specs.square_footage}")
                logger.info(f"  reception_rooms: {sample_specs.reception_rooms}")
                logger.info(f"  epc_rating: {sample_specs.epc_rating}")
            else:
                logger.warning("No data found in the PropertySpecs table!")
                
                # Check if the table exists
                connection = db.engine.connect()
                result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'property_specs')"))
                table_exists = result.scalar()
                logger.info(f"PropertySpecs table exists: {table_exists}")
            
            # Check if any properties have address or specs data
            properties_with_address = Property.query.filter(
                (Property.house_number.isnot(None)) | 
                (Property.street.isnot(None))
            ).count()
            
            properties_with_specs = Property.query.filter(
                (Property.property_type.isnot(None)) | 
                (Property.square_footage.isnot(None))
            ).count()
            
            logger.info(f"Properties with address data: {properties_with_address}")
            logger.info(f"Properties with specs data: {properties_with_specs}")
            
        except Exception as e:
            logger.error(f"Error checking data: {str(e)}")
            raise

if __name__ == "__main__":
    check_data() 