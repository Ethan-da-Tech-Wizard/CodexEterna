# Program: CodexEterna - init_db.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Command-line script that creates all database tables for the Sports Data Service and logs which tables exist.
"""
Database initialization script
Run this to create database tables
"""
# --- Imports ---
import sys
import os

# Add parent directory to path
# Make the folder holding this script importable so 'models' resolves no matter where the script is run from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db, engine, Base
import logging

# --- Logging setup: INFO level so progress messages are visible on the console ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Entry point ---
def main():
    """Initialize the database"""
    logger.info("=" * 60)
    logger.info("Sports Data Service - Database Initialization")
    logger.info("=" * 60)

    try:
        logger.info("Creating database tables...")
        # Creates every table registered on the SQLAlchemy Base (safe to repeat; existing tables are kept).
        init_db()

        logger.info("\n✓ Database initialized successfully!")
        logger.info(f"✓ Database URL: {engine.url}")
        logger.info("\nTables created:")
        # List each table the models define so the operator can confirm what was created.
        for table in Base.metadata.tables.keys():
            logger.info(f"  - {table}")

        logger.info("\nYou can now start the Sports Data Service.")

    except Exception as e:
        logger.error(f"\n✗ Failed to initialize database: {e}")
        # Non-zero exit code lets shell scripts and Docker detect the failure.
        sys.exit(1)


# Only run when executed directly, not when imported.
if __name__ == "__main__":
    main()
