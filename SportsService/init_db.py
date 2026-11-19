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
# Standard-library imports: sys for sys.path/exit codes, os for path handling.
import sys
import os

# Add parent directory to path
# Make 'models' importable regardless of the working directory the script is
# launched from (the Dockerfile CMD runs it as `python init_db.py` from /app).
# Inserted at index 0 so this directory wins over any same-named installed package.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imported after the sys.path tweak above on purpose. Importing models.database
# also creates the SQLAlchemy engine as a side effect (see DATABASE_URL there).
from models.database import init_db, engine, Base
import logging

# Configure root logging once; INFO shows the progress messages below.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Step 1: Execute DDL table creation and report database connectivity status
# Entry point: create every table registered on Base.metadata.
# Exits with status 1 on any failure so `python init_db.py && uvicorn ...` in the
# Dockerfile CMD stops the container instead of starting without a schema.
def main():
    """Initialize the database"""
    logger.info("=" * 60)
    logger.info("Sports Data Service - Database Initialization")
    logger.info("=" * 60)

    try:
        logger.info("Creating database tables...")
        # init_db() runs Base.metadata.create_all, which is idempotent: existing tables
        # are left untouched and only missing ones are created (no migrations).
        init_db()

        logger.info("\n✓ Database initialized successfully!")
        logger.info(f"✓ Database URL: {engine.url}")
        logger.info("\nTables created:")
        # Report which tables are registered so an operator can confirm the schema.
        for table in Base.metadata.tables.keys():
            logger.info(f"  - {table}")

        logger.info("\nYou can now start the Sports Data Service.")

    # Broad catch is deliberate: any failure (bad URL, DB down, permissions) must
    # produce a clear message and a non-zero exit code.
    except Exception as e:
        logger.error(f"\n✗ Failed to initialize database: {e}")
        sys.exit(1)


# Only run when executed as a script, not when imported.
if __name__ == "__main__":
    main()
