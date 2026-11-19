"""
Environment-driven configuration for the Sports Data Service.

Kept free of SQLAlchemy/FastAPI imports so it can be unit-tested without those packages
installed (see tests/test_config.py).

Environment variables
---------------------
DATABASE_URL        Required. SQLAlchemy URL, e.g. postgresql://postgres:<password>@sportsdb:5432/sportsdata.
                    There is deliberately NO default: a built-in password would end up in every
                    deployment that forgot to override it.
CORS_ALLOWED_ORIGINS Optional. Comma-separated list of browser origins allowed to call the API,
                    e.g. "http://localhost:5000,http://localhost:3000". Default: the local
                    PingService dashboard origins only. "*" is rejected.
ADMIN_API_KEY       Optional but required to use destructive routes (DELETE /api/sports/cleanup).
                    When unset the destructive route is disabled (HTTP 503) instead of open.
"""
import hmac
import os
from typing import List, Mapping, Optional

# Origins used when CORS_ALLOWED_ORIGINS is unset: the PingService dashboard served by
# docker-compose (port 5000) on the loopback names a developer would use.
DEFAULT_CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]


def get_database_url(env: Optional[Mapping[str, str]] = None) -> str:
    """
    Return the database URL from the environment.

    Args:
        env: Mapping to read from; defaults to os.environ (parameter exists for tests).

    Returns:
        The DATABASE_URL value.

    Raises:
        RuntimeError: if DATABASE_URL is missing or blank. The message says how to set it, so
            a misconfigured container fails at startup with an actionable error rather than
            connecting with a guessable default password.
    """
    env = os.environ if env is None else env
    url = (env.get("DATABASE_URL") or "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env, set POSTGRES_PASSWORD, "
            "and start the stack with docker compose (which builds DATABASE_URL from it)."
        )
    return url


def get_cors_origins(env: Optional[Mapping[str, str]] = None) -> List[str]:
    """
    Return the list of allowed CORS origins.

    Args:
        env: Mapping to read from; defaults to os.environ.

    Returns:
        Origins parsed from CORS_ALLOWED_ORIGINS (comma separated, whitespace trimmed, empty
        entries ignored), or DEFAULT_CORS_ORIGINS when unset/blank.

    Raises:
        ValueError: if any entry is "*". A wildcard combined with allow_credentials is the
            exact misconfiguration this setting exists to prevent, so it is refused loudly.
    """
    env = os.environ if env is None else env
    raw = env.get("CORS_ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        return list(DEFAULT_CORS_ORIGINS)
    if "*" in origins:
        raise ValueError("CORS_ALLOWED_ORIGINS must list explicit origins; '*' is not allowed")
    return origins


def admin_key_configured(env: Optional[Mapping[str, str]] = None) -> bool:
    """Return True when ADMIN_API_KEY is set to a non-blank value."""
    env = os.environ if env is None else env
    return bool((env.get("ADMIN_API_KEY") or "").strip())


def is_valid_admin_key(provided: Optional[str], env: Optional[Mapping[str, str]] = None) -> bool:
    """
    Check a client-supplied key against ADMIN_API_KEY.

    Args:
        provided: Value of the X-API-Key request header (may be None).
        env: Mapping to read from; defaults to os.environ.

    Returns:
        True only if a key is configured AND matches. Comparison uses hmac.compare_digest so
        response timing does not leak how many leading characters were correct.
    """
    env = os.environ if env is None else env
    expected = (env.get("ADMIN_API_KEY") or "").strip()
    if not expected or not provided:
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))
