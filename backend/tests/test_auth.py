import uuid
from collections.abc import Iterator
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx2 as httpx
import pytest
from fastapi import Response
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.auth import google
from app.auth.sessions import SESSION_COOKIE, set_session_cookie
from app.config import Settings, get_settings
from app.encryption import decrypt
from app.models import OAuthAccount, User

FRONTEND_URL = "http://localhost:3000"
ALL_SCOPES = " ".join(google.SCOPES)


class FakeGoogle:
    """Stands in for Google's token and userinfo endpoints."""

    def __init__(self) -> None:
        self.token_status = 200
        self.tokens: dict[str, Any] = {
            "access_token": "access-token-1",
            "refresh_token": "refresh-token-1",
            "expires_in": 3599,
            "scope": ALL_SCOPES,
            "token_type": "Bearer",
        }
        self.profile: dict[str, Any] = {
            "sub": "google-user-1",
            "email": "ada@example.com",
            "email_verified": True,
            "name": "Ada Lovelace",
        }
        self.token_requests: list[httpx.Request] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        if str(request.url) == google.TOKEN_URL:
            self.token_requests.append(request)
            return httpx.Response(self.token_status, json=self.tokens)
        if str(request.url) == google.USERINFO_URL:
            assert request.headers["Authorization"] == f"Bearer {self.tokens['access_token']}"
            return httpx.Response(200, json=self.profile)
        return httpx.Response(404)


@pytest.fixture
def fake_google(client: TestClient) -> FakeGoogle:
    fake = FakeGoogle()

    def http_client() -> Iterator[httpx.Client]:
        with httpx.Client(transport=httpx.MockTransport(fake.handle)) as http:
            yield http

    client.app.dependency_overrides[google.get_http_client] = http_client
    return fake


def start_sign_in(client: TestClient, **params: str) -> dict[str, str]:
    """Visits the login route and returns the query of the Google URL it redirects to."""
    response = client.get("/api/auth/google/login", params=params)

    assert response.status_code == 302
    location = urlsplit(response.headers["location"])
    assert f"{location.scheme}://{location.netloc}{location.path}" == google.AUTHORIZATION_URL
    return {key: values[0] for key, values in parse_qs(location.query).items()}


def sign_in(client: TestClient) -> httpx.Response:
    """Runs the whole sign-in, as if the user agreed on Google's consent screen."""
    google_params = start_sign_in(client)
    return client.get(
        "/api/auth/google/callback", params={"code": "auth-code", "state": google_params["state"]}
    )


def test_login_redirects_to_google_with_pkce_and_offline_access(client: TestClient) -> None:
    params = start_sign_in(client)

    assert params["client_id"] == "test-client-id.apps.googleusercontent.com"
    assert params["redirect_uri"] == "http://localhost:8000/api/auth/google/callback"
    assert params["response_type"] == "code"
    assert params["scope"].split() == list(google.SCOPES)
    assert params["access_type"] == "offline"
    assert params["code_challenge_method"] == "S256"
    assert len(params["state"]) >= 32
    assert "prompt" not in params


def test_login_shows_consent_screen_again_when_reconnecting(client: TestClient) -> None:
    params = start_sign_in(client, reconnect="true")

    assert params["prompt"] == "consent"


def test_sign_in_explains_when_google_is_not_set_up(client: TestClient) -> None:
    without_google = Settings(google_client_id=None, google_client_secret=None)
    client.app.dependency_overrides[get_settings] = lambda: without_google

    login = client.get("/api/auth/google/login")
    callback = client.get("/api/auth/google/callback", params={"code": "c", "state": "s"})

    for response in (login, callback):
        assert response.status_code == 302
        assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=not_configured"


def test_sign_in_creates_user_and_stores_encrypted_tokens(
    client: TestClient, fake_google: FakeGoogle, db: Session
) -> None:
    google_params = start_sign_in(client)
    response = client.get(
        "/api/auth/google/callback", params={"code": "auth-code", "state": google_params["state"]}
    )

    assert response.status_code == 302
    assert response.headers["location"] == f"{FRONTEND_URL}/"
    assert SESSION_COOKIE in response.cookies

    # The code is exchanged with the PKCE verifier that matches the challenge we sent.
    [token_request] = fake_google.token_requests
    form = {key: values[0] for key, values in parse_qs(token_request.content.decode()).items()}
    assert form["grant_type"] == "authorization_code"
    assert form["code"] == "auth-code"
    assert form["client_secret"] == "test-client-secret"
    assert google.code_challenge(form["code_verifier"]) == google_params["code_challenge"]

    user = db.scalars(select(User)).one()
    assert (user.email, user.name) == ("ada@example.com", "Ada Lovelace")
    account = db.scalars(select(OAuthAccount)).one()
    assert account.user_id == user.id
    assert account.provider_account_id == "google-user-1"
    assert account.access_token == "access-token-1"
    assert account.refresh_token == "refresh-token-1"

    # The database itself only holds ciphertext.
    stored_access, stored_refresh = db.execute(
        text("SELECT access_token, refresh_token FROM oauth_accounts")
    ).one()
    assert "access-token-1" not in stored_access
    assert "refresh-token-1" not in stored_refresh
    assert decrypt(stored_refresh) == "refresh-token-1"


def test_me_returns_the_signed_in_user(client: TestClient, fake_google: FakeGoogle) -> None:
    sign_in(client)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert uuid.UUID(body["id"])
    assert body["email"] == "ada@example.com"
    assert body["name"] == "Ada Lovelace"
    assert body["google_connected"] is True


def test_me_requires_sign_in(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_a_forged_session_cookie(client: TestClient, db: Session) -> None:
    user = User(email="ada@example.com")
    db.add(user)
    db.commit()
    client.cookies.set(SESSION_COOKIE, str(user.id))

    assert client.get("/api/auth/me").status_code == 401


def test_logout_ends_the_session(client: TestClient, fake_google: FakeGoogle) -> None:
    sign_in(client)

    response = client.post("/api/auth/logout")

    assert response.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_returning_user_keeps_refresh_token_when_google_omits_it(
    client: TestClient, fake_google: FakeGoogle, db: Session
) -> None:
    sign_in(client)
    fake_google.tokens = {**fake_google.tokens, "access_token": "access-token-2"}
    del fake_google.tokens["refresh_token"]
    fake_google.profile["name"] = "Ada King"

    sign_in(client)

    user = db.scalars(select(User)).one()
    assert user.name == "Ada King"
    account = db.scalars(select(OAuthAccount)).one()
    assert account.access_token == "access-token-2"
    assert account.refresh_token == "refresh-token-1"


def test_google_is_not_connected_without_gmail_and_calendar_access(
    client: TestClient, fake_google: FakeGoogle
) -> None:
    # The user unticked Gmail and Calendar on Google's consent screen.
    fake_google.tokens["scope"] = "openid https://www.googleapis.com/auth/userinfo.email"
    sign_in(client)

    assert client.get("/api/auth/me").json()["google_connected"] is False


def test_callback_rejects_a_state_this_browser_did_not_start(
    client: TestClient, fake_google: FakeGoogle
) -> None:
    start_sign_in(client)

    response = client.get(
        "/api/auth/google/callback", params={"code": "auth-code", "state": "attacker-state"}
    )

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=session_expired"
    assert fake_google.token_requests == []
    assert SESSION_COOKIE not in response.cookies


def test_callback_without_a_sign_in_attempt_fails(
    client: TestClient, fake_google: FakeGoogle
) -> None:
    response = client.get("/api/auth/google/callback", params={"code": "c", "state": "s"})

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=session_expired"
    assert fake_google.token_requests == []


def test_callback_reports_a_cancelled_sign_in(client: TestClient) -> None:
    start_sign_in(client)

    response = client.get("/api/auth/google/callback", params={"error": "access_denied"})

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=access_denied"


def test_callback_handles_google_refusing_the_code(
    client: TestClient, fake_google: FakeGoogle, db: Session
) -> None:
    fake_google.token_status = 400
    fake_google.tokens = {"error": "invalid_grant"}

    response = sign_in(client)

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=google_error"
    assert db.scalars(select(User)).all() == []


def test_callback_rejects_an_unverified_email(
    client: TestClient, fake_google: FakeGoogle, db: Session
) -> None:
    fake_google.profile["email_verified"] = False

    response = sign_in(client)

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=email_not_verified"
    assert db.scalars(select(User)).all() == []


def test_sign_in_attempt_cannot_be_replayed(client: TestClient, fake_google: FakeGoogle) -> None:
    google_params = start_sign_in(client)
    callback_params = {"code": "auth-code", "state": google_params["state"]}
    client.get("/api/auth/google/callback", params=callback_params)

    response = client.get("/api/auth/google/callback", params=callback_params)

    assert response.headers["location"] == f"{FRONTEND_URL}/sign-in?error=session_expired"
    assert len(fake_google.token_requests) == 1


def test_cookies_are_http_only_and_same_site_lax(client: TestClient) -> None:
    response = client.get("/api/auth/google/login")
    cookie = response.headers["set-cookie"].lower()

    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/api/auth/google" in cookie
    # Local development runs over plain HTTP.
    assert "secure" not in cookie


def test_cookies_are_secure_in_production() -> None:
    production = Settings(environment="production")
    response = Response()

    set_session_cookie(response, production, uuid.uuid7())

    assert "secure" in response.headers["set-cookie"].lower()


def test_cors_allows_credentials_from_the_frontend_only(client: TestClient) -> None:
    assert get_settings().frontend_url == FRONTEND_URL

    allowed = client.get("/api/health", headers={"Origin": FRONTEND_URL})
    other = client.get("/api/health", headers={"Origin": "https://evil.example"})

    assert allowed.headers["access-control-allow-origin"] == FRONTEND_URL
    assert allowed.headers["access-control-allow-credentials"] == "true"
    assert "access-control-allow-origin" not in other.headers
