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

    @staticmethod
    def get_filtered_games(
        db: Session,
        league: Optional[str] = None,
        status: Optional[str] = None,
        is_final: Optional[bool] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        close_game_threshold: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        venue: Optional[str] = None,
        home_team: Optional[str] = None,
        away_team: Optional[str] = None,
        sort_by: str = "date",
        ascending: bool = False,
        limit: int = 100
    ) -> List[Game]:
        """
        Get games with comprehensive filtering options

        Args:
            db: Database session
            league: Filter by league
            status: Filter by game status (e.g., "Final", "Q4", "Scheduled")
            is_final: Filter by final/in-progress games
            min_score: Minimum total score (home + away)
            max_score: Maximum total score
            close_game_threshold: Show only close games (score diff <= threshold)
            date_from: Start date for filtering
            date_to: End date for filtering
            venue: Filter by venue name
            home_team: Filter by home team name
            away_team: Filter by away team name
            sort_by: Sort field (date, home_score, away_score, total_score)
            ascending: Sort direction
            limit: Maximum number of games to return

        Returns:
            List of filtered Game objects
        """
        query = db.query(Game)

        # Apply filters
        if league:
            query = query.filter(Game.league == league)

        if status:
            query = query.filter(Game.status.ilike(f"%{status}%"))

        if is_final is not None:
            query = query.filter(Game.is_final == is_final)

        if date_from:
            query = query.filter(Game.date >= date_from)

        if date_to:
            query = query.filter(Game.date <= date_to)

        if venue:
            query = query.filter(Game.venue.ilike(f"%{venue}%"))

        if home_team:
            query = query.filter(Game.home_team.ilike(f"%{home_team}%"))

        if away_team:
            query = query.filter(Game.away_team.ilike(f"%{away_team}%"))

        # Score-based filters (need to be applied to results after query)
        games = query.all()

        if min_score is not None:
            games = [g for g in games if (g.home_score + g.away_score) >= min_score]

        if max_score is not None:
            games = [g for g in games if (g.home_score + g.away_score) <= max_score]

        if close_game_threshold is not None:
            games = [g for g in games if abs(g.home_score - g.away_score) <= close_game_threshold]

        # Sort
        if sort_by == "home_score":
            games = sorted(games, key=lambda g: g.home_score, reverse=not ascending)
        elif sort_by == "away_score":
            games = sorted(games, key=lambda g: g.away_score, reverse=not ascending)
        elif sort_by == "total_score":
            games = sorted(games, key=lambda g: (g.home_score + g.away_score), reverse=not ascending)
        elif sort_by == "score_diff":
            games = sorted(games, key=lambda g: abs(g.home_score - g.away_score), reverse=not ascending)
        else:  # default to date
            games = sorted(games, key=lambda g: g.date, reverse=not ascending)

        logger.info(f"Retrieved {len(games[:limit])} filtered games")
        return games[:limit]

    @staticmethod
    def get_high_scoring_games(
        db: Session,
        threshold: int = 100,
        league: Optional[str] = None,
        limit: int = 50
    ) -> List[Game]:
        """
        Get high-scoring games (total score above threshold)

        Args:
            db: Database session
            threshold: Minimum total score
            league: Optional league filter
            limit: Maximum number of games to return

        Returns:
            List of high-scoring games
        """
        query = db.query(Game).filter(Game.is_final == True)

        if league:
            query = query.filter(Game.league == league)

        games = query.all()
        high_scoring = [g for g in games if (g.home_score + g.away_score) >= threshold]
        high_scoring.sort(key=lambda g: (g.home_score + g.away_score), reverse=True)

        logger.info(f"Retrieved {len(high_scoring[:limit])} high-scoring games (threshold: {threshold})")
        return high_scoring[:limit]

    @staticmethod
    def get_close_games(
        db: Session,
        max_diff: int = 5,
        league: Optional[str] = None,
        limit: int = 50
    ) -> List[Game]:
        """
        Get close games (score difference <= max_diff)

        Args:
            db: Database session
            max_diff: Maximum score difference
            league: Optional league filter
            limit: Maximum number of games to return

        Returns:
            List of close games
        """
        query = db.query(Game).filter(Game.is_final == True)

        if league:
            query = query.filter(Game.league == league)

        games = query.all()
        close_games = [g for g in games if abs(g.home_score - g.away_score) <= max_diff]
        close_games.sort(key=lambda g: abs(g.home_score - g.away_score))

        logger.info(f"Retrieved {len(close_games[:limit])} close games (max diff: {max_diff})")
        return close_games[:limit]

    @staticmethod
    def get_games_by_status(
        db: Session,
        status_filter: str,
        league: Optional[str] = None,
        limit: int = 100
    ) -> List[Game]:
        """
        Get games by status (Live, Final, Scheduled, etc.)

        Args:
            db: Database session
            status_filter: Status to filter by
            league: Optional league filter
            limit: Maximum number of games to return

        Returns:
            List of games with matching status
        """
        query = db.query(Game).filter(Game.status.ilike(f"%{status_filter}%"))

        if league:
            query = query.filter(Game.league == league)

        games = query.order_by(Game.date.desc()).limit(limit).all()

        logger.info(f"Retrieved {len(games)} games with status: {status_filter}")
        return games

    @staticmethod
    def get_aggregate_stats(
        db: Session,
        group_by: str = "league"
    ) -> dict:
        """
        Get aggregate statistics grouped by various dimensions

        Args:
            db: Database session
            group_by: Grouping dimension (league, status, date)

        Returns:
            Dictionary of aggregate statistics
        """
        stats = {}

        if group_by == "league":
            from sqlalchemy import func
            results = (
                db.query(Game.league, func.count(Game.id))
                .group_by(Game.league)
                .all()
            )
            stats = {league: count for league, count in results}

        elif group_by == "status":
            from sqlalchemy import func
            results = (
                db.query(Game.status, func.count(Game.id))
                .group_by(Game.status)
                .all()
            )
            stats = {status: count for status, count in results}

        elif group_by == "final":
            final_count = db.query(Game).filter(Game.is_final == True).count()
            live_count = db.query(Game).filter(Game.is_final == False).count()
            stats = {"final": final_count, "live": live_count}

        elif group_by == "date":
            # Group by date (last 7 days)
            from sqlalchemy import func
            cutoff = datetime.utcnow() - timedelta(days=7)
            results = (
                db.query(
                    func.date(Game.date).label('game_date'),
                    func.count(Game.id)
                )
                .filter(Game.date >= cutoff)
                .group_by(func.date(Game.date))
                .order_by(func.date(Game.date).desc())
                .all()
            )
            stats = {str(date): count for date, count in results}

        logger.info(f"Generated aggregate stats grouped by: {group_by}")
        return stats


# Singleton instance
game_service = GameService()
