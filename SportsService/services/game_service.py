"""
Game Service - Database operations for games
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models.database import Game, Team
from models.schemas import GameCreate, GameUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameService:
    """
    Service for managing games in the database
    """

    @staticmethod
    def create_or_update_game(db: Session, game_data: dict) -> tuple[Game, bool]:
        """
        Create a new game or update existing one

        Args:
            db: Database session
            game_data: Dictionary containing game data

        Returns:
            Tuple of (Game object, is_new: bool)
        """
        game_id = game_data.get("game_id")

        # Check if game already exists
        existing_game = db.query(Game).filter(Game.game_id == game_id).first()

        if existing_game:
            # Update existing game
            for key, value in game_data.items():
                if hasattr(existing_game, key):
                    setattr(existing_game, key, value)

            existing_game.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_game)

            logger.info(f"Updated game: {game_id}")
            return existing_game, False

        else:
            # Create new game
            new_game = Game(**game_data)
            db.add(new_game)
            db.commit()
            db.refresh(new_game)

            logger.info(f"Created new game: {game_id}")
            return new_game, True

    @staticmethod
    def get_game_by_id(db: Session, game_id: str) -> Optional[Game]:
        """Get a game by its game_id"""
        return db.query(Game).filter(Game.game_id == game_id).first()

    @staticmethod
    def get_games_by_league(
        db: Session,
        league: str,
        limit: int = 100,
        include_final: bool = True
    ) -> List[Game]:
        """
        Get games for a specific league

        Args:
            db: Database session
            league: League identifier
            limit: Maximum number of games to return
            include_final: Whether to include completed games

        Returns:
            List of Game objects
        """
        query = db.query(Game).filter(Game.league == league)

        if not include_final:
            query = query.filter(Game.is_final == False)

        games = query.order_by(Game.date.desc()).limit(limit).all()

        logger.info(f"Retrieved {len(games)} games for league: {league}")
        return games

    @staticmethod
    def get_recent_games(
        db: Session,
        days: int = 7,
        limit: int = 100
    ) -> List[Game]:
        """
        Get games from the last N days

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of games to return

        Returns:
            List of Game objects
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        games = (
            db.query(Game)
            .filter(Game.date >= cutoff_date)
            .order_by(Game.date.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"Retrieved {len(games)} games from last {days} days")
        return games

    @staticmethod
    def get_games_by_team(
        db: Session,
        team_name: str,
        limit: int = 50
    ) -> List[Game]:
        """
        Get games for a specific team

        Args:
            db: Database session
            team_name: Team name (partial match supported)
            limit: Maximum number of games to return

        Returns:
            List of Game objects
        """
        games = (
            db.query(Game)
            .filter(
                (Game.home_team.ilike(f"%{team_name}%")) |
                (Game.away_team.ilike(f"%{team_name}%"))
            )
            .order_by(Game.date.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"Retrieved {len(games)} games for team: {team_name}")
        return games

    @staticmethod
    def delete_old_games(db: Session, days: int = 30) -> int:
        """
        Delete games older than N days

        Args:
            db: Database session
            days: Delete games older than this many days

        Returns:
            Number of games deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        deleted = (
            db.query(Game)
            .filter(Game.date < cutoff_date)
            .delete()
        )

        db.commit()

        logger.info(f"Deleted {deleted} games older than {days} days")
        return deleted

    @staticmethod
    def get_game_count(db: Session, league: Optional[str] = None) -> int:
        """
        Get total number of games

        Args:
            db: Database session
            league: Optional league filter

        Returns:
            Number of games
        """
        query = db.query(Game)

        if league:
            query = query.filter(Game.league == league)

        count = query.count()
        return count


# Singleton instance
game_service = GameService()
