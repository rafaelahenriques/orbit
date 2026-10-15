"""Sign in with Google, and the signed-in session.

The browser visits /google/login, which sends it to Google. Google sends it back to
/google/callback, which signs the user in with a session cookie and returns them to
the dashboard. Failures return them to the dashboard's sign-in page with an error code.
"""

import secrets
import uuid
from typing import Annotated, Literal
from urllib.parse import urlencode

import httpx2 as httpx
from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.auth import google
from app.auth.accounts import can_sync_google, find_google_account, save_google_sign_in
from app.auth.google import GoogleOAuthError
from app.auth.sessions import (
    SIGN_IN_COOKIE,
    SignInAttempt,
    delete_session_cookie,
    delete_sign_in_cookie,
    read_sign_in_cookie,
    set_session_cookie,
    set_sign_in_cookie,
)
from app.config import Settings, get_settings
from app.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

# Shown on the sign-in page, which turns each code into a message.
SignInError = Literal[
    "not_configured", "access_denied", "session_expired", "email_not_verified", "google_error"
]


class SignedInUser(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    # False until the user grants read-only Gmail and Calendar access.
    google_connected: bool


@router.get("/google/login")
def google_login(
    settings: Annotated[Settings, Depends(get_settings)],
    reconnect: bool = False,
) -> RedirectResponse:
    """Sends the browser to Google to sign in. `reconnect` shows Google's consent screen again."""
    if not settings.google_sign_in_enabled:
        return _sign_in_failed(settings, "not_configured")

    attempt = SignInAttempt(state=google.new_state(), code_verifier=google.new_code_verifier())
    url = google.authorization_url(
        settings,
        state=attempt.state,
        code_verifier=attempt.code_verifier,
        ask_for_consent=reconnect,
    )
    response = RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    set_sign_in_cookie(response, settings, attempt)
    return response


@router.get("/google/callback")
def google_callback(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    http: Annotated[httpx.Client, Depends(google.get_http_client)],
    code: Annotated[str | None, Query(max_length=2048)] = None,
    state: Annotated[str | None, Query(max_length=256)] = None,
    error: Annotated[str | None, Query(max_length=256)] = None,
) -> RedirectResponse:
    """Where Google sends the browser back to, with a code to exchange for tokens."""
    if not settings.google_sign_in_enabled:
        return _sign_in_failed(settings, "not_configured")
    if error is not None:
        return _sign_in_failed(
            settings, "access_denied" if error == "access_denied" else "google_error"
        )

    # The state must match the one we sent, which proves this browser started the
    # sign-in. Without this check, an attacker could sign a victim into their account.
    attempt = read_sign_in_cookie(request.cookies.get(SIGN_IN_COOKIE), settings)
    if (
        attempt is None
        or state is None
        or not secrets.compare_digest(state.encode(), attempt.state.encode())
    ):
        return _sign_in_failed(settings, "session_expired")
    if code is None:
        return _sign_in_failed(settings, "google_error")

    try:
        tokens = google.exchange_code(
            http, settings, code=code, code_verifier=attempt.code_verifier
        )
        profile = google.fetch_profile(http, tokens.access_token)
    except GoogleOAuthError:
        return _sign_in_failed(settings, "google_error")

    if not profile.email_verified:
        return _sign_in_failed(settings, "email_not_verified")

    user = save_google_sign_in(db, profile, tokens)

    response = _redirect_to_frontend(settings, "/")
    set_session_cookie(response, settings, user.id)
    delete_sign_in_cookie(response, settings)
    return response


@router.get("/me")
def me(
    user: CurrentUser, db: Annotated[Session, Depends(get_db)], response: Response
) -> SignedInUser:
    """The signed-in user. Responds 401 when nobody is signed in."""
    response.headers["Cache-Control"] = "no-store"
    return SignedInUser(
        id=user.id,
        email=user.email,
        name=user.name,
        google_connected=can_sync_google(find_google_account(db, user)),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(settings: Annotated[Settings, Depends(get_settings)]) -> Response:
    """Signs out of Orbit. Google stays connected, so background sync keeps running."""
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    delete_session_cookie(response, settings)
    return response


def _redirect_to_frontend(settings: Settings, path: str) -> RedirectResponse:
    return RedirectResponse(f"{settings.frontend_url}{path}", status_code=status.HTTP_302_FOUND)


def _sign_in_failed(settings: Settings, reason: SignInError) -> RedirectResponse:
    response = _redirect_to_frontend(settings, f"/sign-in?{urlencode({'error': reason})}")
    # A sign-in attempt is single use, whatever the outcome.
    delete_sign_in_cookie(response, settings)
    return response
