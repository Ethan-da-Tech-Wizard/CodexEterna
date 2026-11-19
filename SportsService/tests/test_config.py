"""Unit tests for models/config.py. Run from SportsService/: python3 -m pytest tests -q"""

# Why these tests exist: models/config.py holds the service's security-sensitive settings (database URL, CORS origins, admin key). Each test pins one rule that must never regress.
# All functions take an explicit env dict instead of reading os.environ, so tests need no monkeypatching and cannot leak settings between each other.
# Run: `python3 -m pytest tests -q` from SportsService/ (pytest is the only test dependency).

import os
import sys

import pytest

# Make 'models' importable the same way init_db.py / the Docker image do.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.config import (  # noqa: E402
    DEFAULT_CORS_ORIGINS,
    admin_key_configured,
    get_cors_origins,
    get_database_url,
    is_valid_admin_key,
)


# Scenario: nothing configured, or only whitespace. The service must refuse to start (RuntimeError) rather than silently use a built-in password.
def test_database_url_has_no_insecure_default():
    # Missing and blank values must both fail: no fallback password may ever be used.
    with pytest.raises(RuntimeError):
        get_database_url({})
    with pytest.raises(RuntimeError):
        get_database_url({"DATABASE_URL": "   "})


# Happy path: the exact configured string is returned unchanged, so credentials and options in it reach the driver untouched.
def test_database_url_read_from_env():
    url = "postgresql://u:p@host:5432/db"
    assert get_database_url({"DATABASE_URL": url}) == url


# Scenario: no CORS variable set. The default must be the local dashboard origins only, and never the wildcard that would let any website call the API from a browser.
def test_cors_defaults_are_local_only():
    assert get_cors_origins({}) == DEFAULT_CORS_ORIGINS
    assert "*" not in get_cors_origins({})


# Scenario: sloppy input (spaces and empty entries from stray commas) is cleaned into exactly the two real origins; sloppy deployment config should not break CORS.
def test_cors_parses_list_and_trims():
    env = {"CORS_ALLOWED_ORIGINS": " https://a.example , https://b.example,, "}
    assert get_cors_origins(env) == ["https://a.example", "https://b.example"]


# Scenario: one wildcard among valid origins. It must raise ValueError even though the other entry is valid, because credentialed requests cannot be combined with "any origin".
def test_cors_wildcard_rejected():
    with pytest.raises(ValueError):
        get_cors_origins({"CORS_ALLOWED_ORIGINS": "https://a.example,*"})


# Scenario: no key configured. Admin endpoints must stay closed to everyone; an empty or missing header must not match an empty configured key.
def test_admin_key_disabled_when_unset():
    # With no key configured nothing may be accepted, not even an empty header.
    assert not admin_key_configured({})
    assert not is_valid_admin_key("anything", {})
    assert not is_valid_admin_key("", {})
    assert not is_valid_admin_key(None, {"ADMIN_API_KEY": "k"})


# Scenario: wrong values (one character off, a prefix) are rejected and only the exact key passes; the near-misses guard against loose comparisons such as startswith.
def test_admin_key_must_match():
    env = {"ADMIN_API_KEY": "s3cret-key"}
    assert admin_key_configured(env)
    assert is_valid_admin_key("s3cret-key", env)
    assert not is_valid_admin_key("s3cret-kez", env)
    assert not is_valid_admin_key("s3cret", env)
