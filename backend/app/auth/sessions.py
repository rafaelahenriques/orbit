"""Signed cookies: the signed-in session, and the short-lived Google sign-in attempt.

Cookie values are signed with SESSION_SECRET, so they cannot be forged or edited.
They are not encrypted, so they hold no secrets of their own.
"""

import uuid
from datetime import timedelta

from fastapi import Response
from itsdangerous import BadSignature, URLSafeTimedSerializer
from pydantic import BaseModel, ValidationError

from app.config import Settings

SESSION_COOKIE = "orbit_session"
SESSION_MAX_AGE = timedelta(days=14)

SIGN_IN_COOKIE = "orbit_google_sign_in"
SIGN_IN_MAX_AGE = timedelta(minutes=10)
# Only Google's redirect back to the callback needs this cookie.
SIGN_IN_COOKIE_PATH = "/api/auth/google"


class SignInAttempt(BaseModel):
    """What we must remember between sending someone to Google and their return."""

    state: str
    code_verifier: str


def _serializer(settings: Settings, purpose: str) -> URLSafeTimedSerializer:
    # A different salt per purpose stops one kind of cookie being replayed as another.
    return URLSafeTimedSerializer(settings.session_secret.get_secret_value(), salt=purpose)


def _set_cookie(
    response: Response,
    settings: Settings,
    *,
    key: str,
    value: str,
    max_age: timedelta,
    path: str = "/",
) -> None:
    response.set_cookie(
        key,
        value,
        max_age=int(max_age.total_seconds()),
        path=path,
        # JavaScript cannot read it, so a script injected into the page cannot steal it.
        httponly=True,
        secure=settings.is_production,
        # Lax still sends the cookie when Google redirects back (a top-level GET), but
        # not on cross-site POSTs, which protects state-changing requests from CSRF.
        samesite="lax",
    )


def _delete_cookie(response: Response, settings: Settings, *, key: str, path: str = "/") -> None:
    response.delete_cookie(
        key, path=path, httponly=True, secure=settings.is_production, samesite="lax"
    )


def set_session_cookie(response: Response, settings: Settings, user_id: uuid.UUID) -> None:
    value = _serializer(settings, "session").dumps(str(user_id))
    _set_cookie(response, settings, key=SESSION_COOKIE, value=value, max_age=SESSION_MAX_AGE)


def read_session_cookie(value: str | None, settings: Settings) -> uuid.UUID | None:
    """Returns the signed-in user's ID, or None if the cookie is missing, forged or expired."""
    if not value:
        return None
    try:
        user_id = _serializer(settings, "session").loads(
            value, max_age=SESSION_MAX_AGE.total_seconds()
        )
        return uuid.UUID(user_id)
    except BadSignature, TypeError, ValueError:
        return None


def delete_session_cookie(response: Response, settings: Settings) -> None:
    _delete_cookie(response, settings, key=SESSION_COOKIE)


def set_sign_in_cookie(response: Response, settings: Settings, attempt: SignInAttempt) -> None:
    value = _serializer(settings, "google-sign-in").dumps(attempt.model_dump())
    _set_cookie(
        response,
        settings,
        key=SIGN_IN_COOKIE,
        value=value,
        max_age=SIGN_IN_MAX_AGE,
        path=SIGN_IN_COOKIE_PATH,
    )


def read_sign_in_cookie(value: str | None, settings: Settings) -> SignInAttempt | None:
    """Returns the pending sign-in, or None if the cookie is missing, forged or expired."""
    if not value:
        return None
    try:
        data = _serializer(settings, "google-sign-in").loads(
            value, max_age=SIGN_IN_MAX_AGE.total_seconds()
        )
        return SignInAttempt.model_validate(data)
    except BadSignature, ValidationError:
        return None


def delete_sign_in_cookie(response: Response, settings: Settings) -> None:
    _delete_cookie(response, settings, key=SIGN_IN_COOKIE, path=SIGN_IN_COOKIE_PATH)
