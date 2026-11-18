# Program: CodexEterna - database.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Defines the SQLAlchemy engine, session factory, the Game and Team table models, and helpers to create tables and hand out sessions.
"""
Database models and configuration for Sports Data Service
"""
# --- Imports ---
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# --- Database connection setup ---
# Database URL comes from the DATABASE_URL environment variable; the fallback is a PostgreSQL URL for the Docker setup.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:secret@sportsdb:5432/sportsdata"
)

# The engine is the shared connection pool; echo=True prints every SQL statement to the log.
# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every table model below inherits from Base so SQLAlchemy can track it.
# Create Base class
Base = declarative_base()


# --- Table models ---
class Game(Base):
    """
    Represents a sports game/match
    """
    # Name of the table in the database.
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    # External id from the data provider; unique so a game is stored only once.
    game_id = Column(String, unique=True, index=True, nullable=False)
    league = Column(String, index=True, nullable=False)
    sport = Column(String, index=True, nullable=False)

    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    # Scores start at 0 until the provider reports otherwise.
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)

    status = Column(String, nullable=False)  # e.g., "Final", "Q4 2:00", "Scheduled"
    date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=True)

    # Flag set once the game has finished.
    is_final = Column(Boolean, default=False)
    # Row timestamps in UTC; updated_at refreshes automatically on every update.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Readable text form used in logs and the debugger.
    def __repr__(self):
        return f"<Game {self.home_team} vs {self.away_team} ({self.league})>"


class Team(Base):
    """
    Represents a sports team
    """
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    abbreviation = Column(String, nullable=True)
    league = Column(String, index=True, nullable=False)

    # Season record counters.
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Team {self.display_name} ({self.league})>"


# --- Helpers ---
def init_db():
    """
    Initialize database - create all tables
    """
    # Create any missing tables; existing ones are left untouched.
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


# Generator used as a FastAPI dependency: opens a session per request.
def get_db():
    """
    Dependency to get database session
    """
    # One session per request.
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always release the connection, even if the request failed.
        db.close()
