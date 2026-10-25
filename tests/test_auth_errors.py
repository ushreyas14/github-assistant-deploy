"""Tests for the friendly-auth-error mapping used by backend/routers/auth.py.

Importing this module does not touch the network: Supabase clients are only
created lazily, inside request handlers.
"""

from backend.routers.auth import _friendly_auth_error


def test_signup_duplicate_account_returns_409():
    status, detail = _friendly_auth_error(
        "signup", Exception("User already registered")
    )
    assert status == 409
    assert "already exists" in detail.lower()


def test_signup_generic_failure_returns_400():
    status, detail = _friendly_auth_error("signup", Exception("boom"))
    assert status == 400


def test_login_invalid_credentials_returns_401():
    status, detail = _friendly_auth_error(
        "login", Exception("Invalid login credentials")
    )
    assert status == 401
    assert "invalid email or password" in detail.lower()


def test_login_unconfirmed_email_returns_401():
    status, detail = _friendly_auth_error(
        "login", Exception("Email not confirmed")
    )
    assert status == 401
    assert "confirm your email" in detail.lower()


def test_unknown_operation_returns_generic_400():
    status, detail = _friendly_auth_error("reset", Exception("whatever"))
    assert status == 400
    assert detail == "Authentication failed."
