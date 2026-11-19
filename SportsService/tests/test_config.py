"""Unit tests for models/config.py. Run from SportsService/: python3 -m pytest tests -q"""
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


def test_database_url_has_no_insecure_default():
    # Missing and blank values must both fail: no fallback password may ever be used.
    with pytest.raises(RuntimeError):
        get_database_url({})
    with pytest.raises(RuntimeError):
        get_database_url({"DATABASE_URL": "   "})


def test_database_url_read_from_env():
    url = "postgresql://u:p@host:5432/db"
    assert get_database_url({"DATABASE_URL": url}) == url


def test_cors_defaults_are_local_only():
    assert get_cors_origins({}) == DEFAULT_CORS_ORIGINS
    assert "*" not in get_cors_origins({})


def test_cors_parses_list_and_trims():
    env = {"CORS_ALLOWED_ORIGINS": " https://a.example , https://b.example,, "}
    assert get_cors_origins(env) == ["https://a.example", "https://b.example"]


def test_cors_wildcard_rejected():
    with pytest.raises(ValueError):
        get_cors_origins({"CORS_ALLOWED_ORIGINS": "https://a.example,*"})


def test_admin_key_disabled_when_unset():
    # With no key configured nothing may be accepted, not even an empty header.
    assert not admin_key_configured({})
    assert not is_valid_admin_key("anything", {})
    assert not is_valid_admin_key("", {})
    assert not is_valid_admin_key(None, {"ADMIN_API_KEY": "k"})


def test_admin_key_must_match():
    env = {"ADMIN_API_KEY": "s3cret-key"}
    assert admin_key_configured(env)
    assert is_valid_admin_key("s3cret-key", env)
    assert not is_valid_admin_key("s3cret-kez", env)
    assert not is_valid_admin_key("s3cret", env)
