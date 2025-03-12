#!/usr/bin/env python3
"""
Script to run the schema migration to add new columns to the Property table.
"""

import sys
import logging
from migrations.add_property_columns import add_columns

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting schema migration to add columns to Property table...")
    
    try:
        add_columns()
        logger.info("Schema migration completed successfully!")
    except Exception as e:
        logger.error(f"Schema migration failed: {str(e)}")
        sys.exit(1)
    
    logger.info("Schema migration process finished.")
    sys.exit(0) 