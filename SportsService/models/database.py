"""
Database models and configuration for Sports Data Service
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Default to SQLite so the app works with zero external dependencies.
# Override with DATABASE_URL env var to use PostgreSQL in production/Docker.
_default_db = "sqlite:///./sportsdata.db"
DATABASE_URL = os.getenv("DATABASE_URL", _default_db)

# SQLite needs check_same_thread=False; PostgreSQL ignores extra connect_args
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


class Game(Base):
    """
    Represents a sports game/match
    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, index=True, nullable=False)
    league = Column(String, index=True, nullable=False)
    sport = Column(String, index=True, nullable=False)

    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)

    status = Column(String, nullable=False)  # e.g., "Final", "Q4 2:00", "Scheduled"
    date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=True)

    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Team {self.display_name} ({self.league})>"


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
