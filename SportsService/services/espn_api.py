# Program: CodexEterna - espn_api.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Client for ESPN's public scoreboard and standings endpoints that turns the JSON into simple game dictionaries.
"""
ESPN API Service - Fetches sports data from ESPN's unofficial API
"""
# --- Imports ---
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- ESPN client ---
class ESPNAPIService:
    """
    Service for fetching sports data from ESPN API
    """

    # Root of the ESPN site API; sport and league are appended to build each request URL.
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

    # Sport mappings
    SPORT_MAPPINGS = {
        # Maps the caller-facing league key to the (sport, league code) pair used in the URL.
        "football/nfl": ("football", "nfl"),
        "basketball/nba": ("basketball", "nba"),
        "baseball/mlb": ("baseball", "mlb"),
        "hockey/nhl": ("hockey", "nhl"),
        "soccer/usa.1": ("soccer", "usa.1"),
        "basketball/wnba": ("basketball", "wnba"),
    }

    # Create one reusable HTTP session so connections are pooled across requests.
    def __init__(self):
        """Create the HTTP session used for every ESPN request"""
        self.session = requests.Session()
        self.session.headers.update({
            # Send a browser-like User-Agent header, since the endpoint is unofficial.
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
        # Reject leagues we have no mapping for before making a network call.
        if league not in self.SPORT_MAPPINGS:
            raise ValueError(f"Unsupported league: {league}")

        sport, league_code = self.SPORT_MAPPINGS[league]
        # Build the scoreboard URL for this league.
        url = f"{self.BASE_URL}/{sport}/{league_code}/scoreboard"

        logger.info(f"Fetching scoreboard from: {url}")

        try:
            # Time out after 10 seconds so a slow server cannot hang the service.
            response = self.session.get(url, timeout=10)
            # Turn HTTP error codes (4xx/5xx) into exceptions.
            response.raise_for_status()
            data = response.json()

            # Convert the raw JSON into our flat game dictionaries.
            games = self._parse_scoreboard(data, league, sport)
            logger.info(f"Successfully fetched {len(games)} games from {league}")

            return games

        # Network or HTTP failure: log it and let the caller decide what to do.
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
        # Collect successfully parsed games here.
        games = []

        # Each scoreboard entry is an 'event' (one game); missing key means no games.
        events = data.get("events", [])

        for event in events:
            try:
                game = self._parse_event(event, league, sport)
                if game:
                    games.append(game)
            # One malformed event should not discard the rest, so log it and move on.
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
            # Pull the basic fields from the event.
            game_id = event.get("id")
            status = event.get("status", {})
            status_type = status.get("type", {}).get("description", "Unknown")

            # Extract date
            date_str = event.get("date")
            # Replace the trailing 'Z' (UTC) with an explicit offset so fromisoformat accepts it; fall back to now if absent.
            game_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else datetime.utcnow()

            # Extract venue
            # The venue and teams live inside the first 'competition' of the event.
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
                # Scores arrive as text; convert to a number.
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
            # Treat regulation, overtime and shootout finals as finished games.
            is_final = status_type.lower() in ["final", "final/ot", "final/so"]

            # Build game dictionary
            # The flat dictionary matches the columns of the Game table.
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

            # Note: the raw JSON is returned unparsed.
            # This is a simplified parser - ESPN standings can be complex
            # For now, we'll just return the raw data
            logger.info(f"Successfully fetched standings for {league}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching standings: {e}")
            raise


# Singleton instance
# Shared instance imported by the API layer.
espn_api = ESPNAPIService()
