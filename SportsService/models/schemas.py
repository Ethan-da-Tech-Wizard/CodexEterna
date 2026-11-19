# ==============================================================================
# Program: schemas.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 18, 2026
# Purpose: Pydantic schema validation models defining request/response contracts
#          and serialization rules for sports API endpoints.
# ==============================================================================
"""
Pydantic schemas for API request/response validation
"""
# Pydantic v2 base model (Field is imported but not used in this module).
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Step 1: Shared attribute schema for game entity validation
class GameBase(BaseModel):
    """Base game schema"""
    league: str
    sport: str
    home_team: str
    away_team: str
    home_score: int = 0
    away_score: int = 0
    status: str
    date: datetime
    venue: Optional[str] = None


# Input schema for creating a game; adds the externally supplied game_id.
class GameCreate(GameBase):
    """Schema for creating a game"""
    game_id: str


# Partial update: every field is Optional so clients send only what changed;
# unset fields (None) mean 'leave unchanged'.
class GameUpdate(BaseModel):
    """Schema for updating a game"""
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: Optional[str] = None
    is_final: Optional[bool] = None


# Step 2: Public API response schema including generated identifiers
class GameResponse(GameBase):
    """Schema for game response"""
    id: int
    game_id: str
    is_final: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        # from_attributes lets Pydantic v2 build this schema straight from an ORM object
        # (replacement for the v1 orm_mode setting).
        from_attributes = True


# Fields shared by team create/response schemas.
class TeamBase(BaseModel):
    """Base team schema"""
    name: str
    display_name: str
    abbreviation: Optional[str] = None
    league: str


# Input schema for creating a team; adds the externally supplied team_id.
class TeamCreate(TeamBase):
    """Schema for creating a team"""
    team_id: str


# Public representation of a stored team, including record and audit timestamps.
class TeamResponse(TeamBase):
    """Schema for team response"""
    id: int
    team_id: str
    wins: int = 0
    losses: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Summary returned by the fetch endpoints so callers can see how many games were
# fetched versus created or updated.
class FetchResponse(BaseModel):
    """Response for fetch operations"""
    success: bool
    message: str
    games_fetched: int = 0
    games_updated: int = 0
    games_created: int = 0


# Payload of GET /health; 'database' reports connectivity of the backing store.
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: datetime
