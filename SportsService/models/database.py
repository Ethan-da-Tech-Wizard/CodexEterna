# ==============================================================================
# Program: database.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 18, 2026
# Purpose: SQLAlchemy ORM entity definitions and database connection engine
#          configuration for the Sports Data Service.
# ==============================================================================
"""
Database models and configuration for Sports Data Service
"""
# SQLAlchemy building blocks: engine factory, column types and the ORM base/session helpers.
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# datetime.utcnow is used as the default for created_at/updated_at timestamps (naive UTC).
from datetime import datetime
import os

# Database URL from environment variable or default to SQLite
# Connection string for SQLAlchemy, read once at import time (later environment changes
# have no effect). NOTE: the comment above says the fallback is SQLite, but it is in fact
# a PostgreSQL URL for the compose service 'sportsdb'. docker-compose.yml also sets
# DATABASE_URL explicitly, so this default only applies outside that setup.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:secret@sportsdb:5432/sportsdata"
)

# Create engine
# Shared engine (connection pool). echo=True logs every SQL statement: handy for
# debugging, but noisy and it can expose data in production logs.
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
# Session factory. autocommit=False means callers must commit explicitly;
# autoflush=False means pending changes are not flushed before each query.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
# Declarative base class; every model below registers its table on Base.metadata.
Base = declarative_base()


# Step 1: Core relational entity storing game scores, timestamps, and status
class Game(Base):
    """
    Represents a sports game/match
    """
    __tablename__ = "games"

    # Surrogate primary key used internally; game_id below is the external ESPN id.
    id = Column(Integer, primary_key=True, index=True)
    # External identifier from ESPN; unique so a re-fetch can update instead of duplicate.
    game_id = Column(String, unique=True, index=True, nullable=False)
    # League key such as 'football/nfl'; indexed because queries filter by league.
    league = Column(String, index=True, nullable=False)
    sport = Column(String, index=True, nullable=False)

    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    # Scores default to 0 so games that have not started still hold valid values.
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)

    status = Column(String, nullable=False)  # e.g., "Final", "Q4 2:00", "Scheduled"
    date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=True)

    # Cached flag derived from the status text so queries need not parse it.
    is_final = Column(Boolean, default=False)
    # Row creation time (naive UTC, set by Python rather than the database).
    created_at = Column(DateTime, default=datetime.utcnow)
    # Refreshed by SQLAlchemy (onupdate) whenever the row is changed through the ORM.
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Game {self.home_team} vs {self.away_team} ({self.league})>"


# Step 2: Relational entity storing franchise information, logos, and records
class Team(Base):
    """
    Represents a sports team
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    # External team identifier; unique and indexed for lookups.
    team_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=True)
    league = Column(String, index=True, nullable=False)

    # Win/loss counters default to 0; they are not currently populated by the fetch path.
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Team {self.display_name} ({self.league})>"


# Create all tables registered on Base.metadata. Idempotent: existing tables are skipped.
# No schema migrations are performed, so column changes need a manual migration.
def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


# FastAPI dependency: yields one session per request and always closes it afterwards,
# returning the connection to the pool even if the handler raises.
def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
