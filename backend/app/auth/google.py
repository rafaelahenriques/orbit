"""Google's OAuth 2.0 authorization code flow, with PKCE.

See https://developers.google.com/identity/protocols/oauth2/web-server
"""

import base64
import hashlib
import logging
import secrets
from collections.abc import Iterator
from urllib.parse import urlencode

import httpx2 as httpx
from pydantic import BaseModel, ValidationError

from app.config import Settings

logger = logging.getLogger(__name__)

PROVIDER = "google"

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
CALENDAR_EVENTS_READONLY = "https://www.googleapis.com/auth/calendar.events.readonly"

# Read-only access that background sync needs, in addition to signing in.
SYNC_SCOPES = frozenset({GMAIL_READONLY, CALENDAR_EVENTS_READONLY})
SCOPES = ("openid", "email", "profile", GMAIL_READONLY, CALENDAR_EVENTS_READONLY)


class GoogleOAuthError(Exception):
    """Google refused a request or sent a response we could not use."""


class GoogleTokens(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    # Only sent when the user gives consent, not on every sign-in.
    refresh_token: str | None = None


class GoogleProfile(BaseModel):
    sub: str
    email: str
    email_verified: bool = False
    name: str | None = None


def get_http_client() -> Iterator[httpx.Client]:
    """FastAPI dependency for calls to Google, replaced with a fake in tests."""
    with httpx.Client(timeout=10) as client:
        yield client


def new_state() -> str:
    return secrets.token_urlsafe(32)


def new_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def authorization_url(
    settings: Settings, *, state: str, code_verifier: str, ask_for_consent: bool
) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        # Offline access returns a refresh token, so sync can run while the user is away.
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": state,
        "code_challenge": code_challenge(code_verifier),
        "code_challenge_method": "S256",
    }
    if ask_for_consent:
        # Shows the consent screen again even if the user already agreed, so they can
        # grant missing scopes and Google issues a new refresh token.
        params["prompt"] = "consent"
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"


def exchange_code(
    http: httpx.Client, settings: Settings, *, code: str, code_verifier: str
) -> GoogleTokens:
    response = _send(
        http,
        "POST",
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.google_redirect_uri,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret.get_secret_value(),
        },
    )
    return _parse(GoogleTokens, response)


def fetch_profile(http: httpx.Client, access_token: str) -> GoogleProfile:
    response = _send(http, "GET", USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
    return _parse(GoogleProfile, response)


def _send(http: httpx.Client, method: str, url: str, **kwargs: object) -> httpx.Response:
    try:
        response = http.request(method, url, **kwargs)
    except httpx.HTTPError as error:
        raise GoogleOAuthError(f"Could not reach Google: {error.__class__.__name__}") from None
    if response.is_error:
        # Google's error responses hold an error code, never tokens, so they are safe to log.
        logger.warning("Google returned %s for %s: %s", response.status_code, url, response.text)
        raise GoogleOAuthError(f"Google returned {response.status_code}")
    return response


def _parse[ModelT: BaseModel](model: type[ModelT], response: httpx.Response) -> ModelT:
    try:
        return model.model_validate_json(response.content)
    except ValidationError:
        raise GoogleOAuthError(f"Unexpected response from Google: {model.__name__}") from None
