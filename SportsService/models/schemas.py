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


class GameCreate(GameBase):
    """Schema for creating a game"""
    game_id: str


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
        from_attributes = True


class TeamBase(BaseModel):
    """Base team schema"""
    name: str
    display_name: str
    abbreviation: Optional[str] = None
    league: str


class TeamCreate(TeamBase):
    """Schema for creating a team"""
    team_id: str


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


class FetchResponse(BaseModel):
    """Response for fetch operations"""
    success: bool
    message: str
    games_fetched: int = 0
    games_updated: int = 0
    games_created: int = 0


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: datetime
