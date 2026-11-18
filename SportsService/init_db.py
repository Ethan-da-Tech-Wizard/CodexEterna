# ==============================================================================
# Program: init_db.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 18, 2026
# Purpose: Standalone database initialization CLI script creating relational schema
#          tables for games, teams, and tournament metadata.
# ==============================================================================
"""
Database initialization script
Run this to create database tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Step 1: Execute DDL table creation and report database connectivity status
def main():
    """Initialize the database"""
    logger.info("=" * 60)
    logger.info("Sports Data Service - Database Initialization")
    logger.info("=" * 60)

    try:
        logger.info("Creating database tables...")
        init_db()

        logger.info("\n✓ Database initialized successfully!")
        logger.info(f"✓ Database URL: {engine.url}")
        logger.info("\nTables created:")
        for table in Base.metadata.tables.keys():
            logger.info(f"  - {table}")

        logger.info("\nYou can now start the Sports Data Service.")

    except Exception as e:
        logger.error(f"\n✗ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
