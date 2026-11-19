# ==============================================================================
# Program: main.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 18, 2026
# Purpose: FastAPI application server providing RESTful endpoints for sports data
#          aggregation from ESPN APIs, persistent PostgreSQL storage, and query filtering.
# ==============================================================================
"""
Sports Data Service - FastAPI Application
Fetches and stores sports data from ESPN API
"""
# FastAPI framework pieces: routing, dependency injection, HTTP errors and query validation.
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

# Absolute imports (models., services.) rely on /app being the working directory
# and on sys.path, as in the Docker image (`uvicorn app.main:app` run from /app).
from models.database import get_db, init_db, engine
from models.schemas import (
    GameResponse,
    FetchResponse,
    HealthResponse
)
from services.espn_api import espn_api
from services.game_service import game_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
# The ASGI application object; uvicorn imports it as app.main:app.
app = FastAPI(
    title="Sports Data Service",
    description="Real-time sports data aggregation from ESPN API with persistent storage",
    version="1.0.0"
)

# Add CORS middleware
# SECURITY NOTE: origins/methods/headers are all '*' while credentials are allowed.
# That is convenient for local development but too permissive for a public deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Step 1: Initialize database schema and verify table availability on startup
@app.on_event("startup")
# Runs once when the server starts. Table creation is idempotent, so it is safe even
# though the Docker CMD already ran init_db.py. @app.on_event is deprecated in newer
# FastAPI in favour of lifespan handlers but still works.
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Sports Data Service...")
    logger.info("Initializing database...")

    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        # Failure is logged but not fatal: /health will report the database state instead.
        logger.error(f"Failed to initialize database: {e}")
        # Don't crash the app, but log the error


@app.get("/")
# Service index listing the main endpoints; useful as a quick liveness check.
async def root():
    """Root endpoint"""
    return {
        "service": "Sports Data Service",
        "version": "1.0.0",
        "description": "Real-time sports data aggregation",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "fetch_data": "/api/sports/fetch",
            "get_games": "/api/sports/games"
        }
    }


@app.get("/health", response_model=HealthResponse)
# Health probe used by the Docker HEALTHCHECK. Runs a real count query, so it
# returns 503 when the database is unreachable rather than just proving the process is up.
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        game_count = game_service.get_game_count(db)

        return HealthResponse(
            status="healthy",
            database=f"connected ({game_count} games stored)",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/api/sports/fetch", response_model=FetchResponse)
# Pull the current scoreboard for one league from ESPN and upsert every game.
# Note: the ESPN and DB calls are synchronous and run inside an async handler, so they
# block the event loop for their duration.
# Unsupported leagues raise ValueError in the ESPN client and become HTTP 400.
async def fetch_sports_data(
    league: str = Query(..., description="League to fetch (e.g., 'football/nfl', 'basketball/nba')"),
    db: Session = Depends(get_db)
):
    """
    Fetch latest sports data from ESPN API and store in database

    Args:
        league: League identifier (e.g., 'football/nfl', 'basketball/nba')
        db: Database session

    Returns:
        FetchResponse with statistics about the fetch operation
    """
    try:
        logger.info(f"Fetching data for league: {league}")

        # Fetch data from ESPN API
        games_data = espn_api.fetch_scoreboard(league)

        if not games_data:
            return FetchResponse(
                success=True,
                message=f"No games found for {league}",
                games_fetched=0,
                games_updated=0,
                games_created=0
            )

        # Store games in database
        games_created = 0
        games_updated = 0

        # Upsert one game at a time (each call commits); tallies new versus updated rows.
        for game_data in games_data:
            game, is_new = game_service.create_or_update_game(db, game_data)

            if is_new:
                games_created += 1
            else:
                games_updated += 1

        total_games = len(games_data)

        logger.info(
            f"Fetch complete: {total_games} total, "
            f"{games_created} created, {games_updated} updated"
        )

        return FetchResponse(
            success=True,
            message=f"Successfully fetched {total_games} games for {league}",
            games_fetched=total_games,
            games_created=games_created,
            games_updated=games_updated
        )

    # ValueError here means an unsupported league (raised by the ESPN client).
    except ValueError as e:
        logger.error(f"Invalid league: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Error fetching sports data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")


@app.get("/api/sports/games", response_model=List[GameResponse])
# List stored games. Filter precedence is team, then days, then league; only the
# first one supplied is applied. With no filter, the last 7 days are returned.
async def get_games(
    league: Optional[str] = Query(None, description="Filter by league"),
    team: Optional[str] = Query(None, description="Filter by team name"),
    days: Optional[int] = Query(None, description="Get games from last N days"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of games to return"),
    db: Session = Depends(get_db)
):
    """
    Get stored games with optional filters

    Args:
        league: Filter by league
        team: Filter by team name (partial match)
        days: Get games from last N days
        limit: Maximum number of games to return
        db: Database session

    Returns:
        List of GameResponse objects
    """
    try:
        if team:
            games = game_service.get_games_by_team(db, team, limit)
        elif days:
            games = game_service.get_recent_games(db, days, limit)
        elif league:
            games = game_service.get_games_by_league(db, league, limit)
        else:
            # Get all recent games
            games = game_service.get_recent_games(db, 7, limit)

        logger.info(f"Retrieved {len(games)} games")

        return games

    except Exception as e:
        logger.error(f"Error retrieving games: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve games: {str(e)}")


@app.get("/api/sports/game/{game_id}", response_model=GameResponse)
# Fetch one game by its external id; 404 if unknown.
async def get_game(
    game_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific game by ID

    Args:
        game_id: Game identifier
        db: Database session

    Returns:
        GameResponse object
    """
    try:
        game = game_service.get_game_by_id(db, game_id)

        if not game:
            raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")

        return game

    # Re-raise deliberate HTTP errors (e.g. 404) so the generic handler below
    # does not convert them into 500 responses.
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving game: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve game: {str(e)}")


@app.get("/api/sports/filter", response_model=List[GameResponse])
# Advanced search. Dates are accepted as YYYY-MM-DD strings and parsed here;
# date_to is midnight at the start of that day, so games later that day are excluded.
async def get_filtered_games(
    league: Optional[str] = Query(None, description="Filter by league"),
    status: Optional[str] = Query(None, description="Filter by game status"),
    is_final: Optional[bool] = Query(None, description="Filter by final/live games"),
    min_score: Optional[int] = Query(None, description="Minimum total score"),
    max_score: Optional[int] = Query(None, description="Maximum total score"),
    close_game_threshold: Optional[int] = Query(None, description="Show only close games (max score diff)"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    venue: Optional[str] = Query(None, description="Filter by venue name"),
    home_team: Optional[str] = Query(None, description="Filter by home team"),
    away_team: Optional[str] = Query(None, description="Filter by away team"),
    sort_by: str = Query("date", description="Sort by: date, home_score, away_score, total_score, score_diff"),
    ascending: bool = Query(False, description="Sort ascending (default: descending)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of games"),
    db: Session = Depends(get_db)
):
    """
    Get games with comprehensive filtering options

    Filter games by multiple criteria including league, status, scores, dates, and teams.
    Sort results by various fields in ascending or descending order.
    """
    try:
        # Parse dates if provided
        date_from_obj = None
        date_to_obj = None

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")

        games = game_service.get_filtered_games(
            db=db,
            league=league,
            status=status,
            is_final=is_final,
            min_score=min_score,
            max_score=max_score,
            close_game_threshold=close_game_threshold,
            date_from=date_from_obj,
            date_to=date_to_obj,
            venue=venue,
            home_team=home_team,
            away_team=away_team,
            sort_by=sort_by,
            ascending=ascending,
            limit=limit
        )

        logger.info(f"Retrieved {len(games)} filtered games")
        return games

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering games: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to filter games: {str(e)}")


@app.get("/api/sports/high-scoring", response_model=List[GameResponse])
# Finished games with combined score at or above the threshold (50-300 allowed).
async def get_high_scoring_games(
    threshold: int = Query(100, ge=50, le=300, description="Minimum total score"),
    league: Optional[str] = Query(None, description="Filter by league"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of games"),
    db: Session = Depends(get_db)
):
    """
    Get high-scoring games above a threshold

    Shows games with combined scores exceeding the specified threshold.
    Sorted by total score (highest first).
    """
    try:
        games = game_service.get_high_scoring_games(db, threshold, league, limit)
        logger.info(f"Retrieved {len(games)} high-scoring games")
        return games
    except Exception as e:
        logger.error(f"Error retrieving high-scoring games: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve high-scoring games: {str(e)}")


@app.get("/api/sports/close-games", response_model=List[GameResponse])
# Finished games decided by at most max_diff points (1-20 allowed).
async def get_close_games(
    max_diff: int = Query(5, ge=1, le=20, description="Maximum score difference"),
    league: Optional[str] = Query(None, description="Filter by league"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of games"),
    db: Session = Depends(get_db)
):
    """
    Get close games with small score differences

    Shows games where the final score difference is within the specified threshold.
    Sorted by score difference (closest games first).
    """
    try:
        games = game_service.get_close_games(db, max_diff, league, limit)
        logger.info(f"Retrieved {len(games)} close games")
        return games
    except Exception as e:
        logger.error(f"Error retrieving close games: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve close games: {str(e)}")


@app.get("/api/sports/by-status", response_model=List[GameResponse])
# Games whose status text contains the given text (case-insensitive).
async def get_games_by_status(
    status: str = Query(..., description="Status to filter by (e.g., 'Final', 'Live', 'Q4')"),
    league: Optional[str] = Query(None, description="Filter by league"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of games"),
    db: Session = Depends(get_db)
):
    """
    Get games by their status

    Filter games by status: Final, Live, Scheduled, Quarter/Period, etc.
    """
    try:
        games = game_service.get_games_by_status(db, status, league, limit)
        logger.info(f"Retrieved {len(games)} games with status: {status}")
        return games
    except Exception as e:
        logger.error(f"Error retrieving games by status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve games by status: {str(e)}")


@app.get("/api/sports/aggregate")
# Counts of games grouped by league, status, final/live or date.
# The group_by value is validated against a whitelist before reaching the service.
async def get_aggregate_statistics(
    group_by: str = Query("league", description="Group by: league, status, final, date"),
    db: Session = Depends(get_db)
):
    """
    Get aggregate statistics grouped by various dimensions

    - league: Count of games per league
    - status: Count of games per status
    - final: Count of final vs live games
    - date: Count of games per date (last 7 days)
    """
    try:
        valid_groupings = ["league", "status", "final", "date"]
        if group_by not in valid_groupings:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid group_by. Valid options: {', '.join(valid_groupings)}"
            )

        stats = game_service.get_aggregate_stats(db, group_by)
        return {
            "group_by": group_by,
            "stats": stats,
            "timestamp": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting aggregate stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get aggregate stats: {str(e)}")


@app.get("/api/sports/leagues")
# Expose the league whitelist from the ESPN client plus friendly aliases.
async def get_supported_leagues():
    """
    Get list of supported leagues

    Returns:
        Dictionary of supported leagues
    """
    return {
        "supported_leagues": list(espn_api.SPORT_MAPPINGS.keys()),
        "examples": {
            "nfl": "football/nfl",
            "nba": "basketball/nba",
            "mlb": "baseball/mlb",
            "nhl": "hockey/nhl",
            "mls": "soccer/usa.1",
            "wnba": "basketball/wnba"
        }
    }


@app.delete("/api/sports/cleanup")
# Delete games older than N days (1-365). SECURITY NOTE: destructive and has no
# authentication, so it should not be exposed publicly as-is.
async def cleanup_old_games(
    days: int = Query(30, ge=1, le=365, description="Delete games older than N days"),
    db: Session = Depends(get_db)
):
    """
    Delete old games from database

    Args:
        days: Delete games older than this many days
        db: Database session

    Returns:
        Number of games deleted
    """
    try:
        deleted = game_service.delete_old_games(db, days)

        logger.info(f"Cleanup complete: deleted {deleted} games")

        return {
            "success": True,
            "message": f"Deleted {deleted} games older than {days} days",
            "deleted": deleted
        }

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@app.get("/api/sports/stats")
# Overall and per-league game counts. Issues one COUNT query per supported league.
async def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about stored data

    Args:
        db: Database session

    Returns:
        Statistics dictionary
    """
    try:
        total_games = game_service.get_game_count(db)

        # Get counts by league
        leagues = espn_api.SPORT_MAPPINGS.keys()
        league_counts = {}

        for league in leagues:
            count = game_service.get_game_count(db, league)
            if count > 0:
                league_counts[league] = count

        return {
            "total_games": total_games,
            "games_by_league": league_counts,
            "supported_leagues": list(leagues)
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# Development entry point only; the container runs uvicorn via the Dockerfile CMD.
# reload=True watches for code changes and host 0.0.0.0 listens on all interfaces.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
