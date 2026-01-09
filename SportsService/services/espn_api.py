"""
ESPN API Service - Fetches sports data from ESPN's unofficial API
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ESPNAPIService:
    """
    Service for fetching sports data from ESPN API
    """

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

    # Sport mappings
    SPORT_MAPPINGS = {
        "football/nfl": ("football", "nfl"),
        "basketball/nba": ("basketball", "nba"),
        "baseball/mlb": ("baseball", "mlb"),
        "hockey/nhl": ("hockey", "nhl"),
        "soccer/usa.1": ("soccer", "usa.1"),
        "basketball/wnba": ("basketball", "wnba"),
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def fetch_scoreboard(self, league: str) -> List[Dict]:
        """
        Fetch scoreboard data for a specific league

        Args:
            league: League identifier (e.g., 'football/nfl', 'basketball/nba')

        Returns:
            List of game dictionaries
        """
        if league not in self.SPORT_MAPPINGS:
            raise ValueError(f"Unsupported league: {league}")

        sport, league_code = self.SPORT_MAPPINGS[league]
        url = f"{self.BASE_URL}/{sport}/{league_code}/scoreboard"

        logger.info(f"Fetching scoreboard from: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            games = self._parse_scoreboard(data, league, sport)
            logger.info(f"Successfully fetched {len(games)} games from {league}")

            return games

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching scoreboard: {e}")
            raise

    def _parse_scoreboard(self, data: Dict, league: str, sport: str) -> List[Dict]:
        """
        Parse ESPN scoreboard JSON response

        Args:
            data: JSON response from ESPN API
            league: League identifier
            sport: Sport type

        Returns:
            List of parsed game dictionaries
        """
        games = []

        events = data.get("events", [])

        for event in events:
            try:
                game = self._parse_event(event, league, sport)
                if game:
                    games.append(game)
            except Exception as e:
                logger.warning(f"Error parsing event: {e}")
                continue

        return games

    def _parse_event(self, event: Dict, league: str, sport: str) -> Optional[Dict]:
        """
        Parse a single event/game from ESPN API

        Args:
            event: Event dictionary from ESPN API
            league: League identifier
            sport: Sport type

        Returns:
            Parsed game dictionary or None
        """
        try:
            # Extract basic info
            game_id = event.get("id")
            status = event.get("status", {})
            status_type = status.get("type", {}).get("description", "Unknown")

            # Extract date
            date_str = event.get("date")
            game_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else datetime.utcnow()

            # Extract venue
            competitions = event.get("competitions", [])
            if not competitions:
                return None

            competition = competitions[0]
            venue = competition.get("venue", {}).get("fullName", "")

            # Extract competitors (teams)
            competitors = competition.get("competitors", [])
            if len(competitors) < 2:
                return None

            # ESPN typically has home team first, away team second
            # But check the 'homeAway' field to be sure
            home_team = None
            away_team = None

            for competitor in competitors:
                team_info = competitor.get("team", {})
                team_name = team_info.get("displayName", "Unknown")
                score = int(competitor.get("score", 0))
                is_home = competitor.get("homeAway") == "home"

                if is_home:
                    home_team = {"name": team_name, "score": score}
                else:
                    away_team = {"name": team_name, "score": score}

            if not home_team or not away_team:
                # Fallback: assume first is home, second is away
                home_team = {
                    "name": competitors[0].get("team", {}).get("displayName", "Unknown"),
                    "score": int(competitors[0].get("score", 0))
                }
                away_team = {
                    "name": competitors[1].get("team", {}).get("displayName", "Unknown"),
                    "score": int(competitors[1].get("score", 0))
                }

            # Determine if game is final
            is_final = status_type.lower() in ["final", "final/ot", "final/so"]

            # Build game dictionary
            game = {
                "game_id": str(game_id),
                "league": league,
                "sport": sport,
                "home_team": home_team["name"],
                "away_team": away_team["name"],
                "home_score": home_team["score"],
                "away_score": away_team["score"],
                "status": status_type,
                "date": game_date,
                "venue": venue,
                "is_final": is_final
            }

            return game

        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None

    def fetch_team_standings(self, league: str) -> List[Dict]:
        """
        Fetch team standings for a league

        Args:
            league: League identifier

        Returns:
            List of team standings
        """
        if league not in self.SPORT_MAPPINGS:
            raise ValueError(f"Unsupported league: {league}")

        sport, league_code = self.SPORT_MAPPINGS[league]
        url = f"{self.BASE_URL}/{sport}/{league_code}/standings"

        logger.info(f"Fetching standings from: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # This is a simplified parser - ESPN standings can be complex
            # For now, we'll just return the raw data
            logger.info(f"Successfully fetched standings for {league}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching standings: {e}")
            raise


# Singleton instance
espn_api = ESPNAPIService()
