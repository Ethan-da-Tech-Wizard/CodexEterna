# Program: CodexEterna - schemas.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Pydantic models that validate and describe the request and response bodies of the Sports Data Service API.
"""
Pydantic schemas for API request/response validation
"""
# --- Imports ---
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# --- Game schemas ---
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


class GameResponse(GameBase):
    """Schema for game response"""
    id: int
    game_id: str
    is_final: bool
    created_at: datetime
    updated_at: datetime

    # Allow building the schema directly from a database object's attributes.
    class Config:
        from_attributes = True


# --- Team schemas ---
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


# --- Operational response schemas ---
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
