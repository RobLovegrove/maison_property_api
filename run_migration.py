#!/usr/bin/env python3
"""
Script to run the migration to combine Property, Address, and PropertySpecs tables.
"""

import sys
import logging
from migrations.combine_property_tables import migrate_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting migration to combine property tables...")
    
    try:
        migrate_data()
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)
    
    logger.info("Migration process finished.")
    sys.exit(0) 