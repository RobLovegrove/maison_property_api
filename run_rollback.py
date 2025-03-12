#!/usr/bin/env python3
"""
Script to rollback the property model migration.
"""

import sys
import logging
from migrations.rollback_property_migration import rollback_migration

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting rollback of property model migration...")
    
    try:
        rollback_migration()
        logger.info("Rollback completed successfully!")
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        sys.exit(1)
    
    logger.info("Rollback process finished.")
    sys.exit(0) 