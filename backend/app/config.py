from functools import lru_cache
from typing import Literal, Self

from cryptography.fernet import Fernet
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables.

    Defaults match the local Docker Compose services so the app runs out of the box
    in development. Deployed environments must set every value explicitly.

    Secrets have no defaults: the app refuses to start until they are set. The Google
    OAuth client is the exception outside production, so the stack can run before
    Google sign-in is set up.
    """

    model_config = SettingsConfigDict(
        # Keep secret values out of validation errors, which end up in logs.
        hide_input_in_errors=True,
        # Treat `KEY=` (as copied from .env.example) the same as a missing value.
        env_ignore_empty=True,
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://orbit:orbit@localhost:5433/orbit"
    redis_url: str = "redis://localhost:6379/0"

    # Where the dashboard runs, without a trailing slash. The API only accepts
    # credentialed browser requests from this origin, and sends people back here
    # after signing in.
    frontend_url: str = "http://localhost:3000"

    # OAuth client from the Google Cloud console. The client ID is public (it is part
    # of the sign-in URL); the secret is not. Without them, sign-in is turned off.
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    # Must exactly match an authorised redirect URI on the Google OAuth client.
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # Signs session cookies. Rotating it signs everyone out.
    session_secret: SecretStr = Field(min_length=32)
    # Fernet key that encrypts Google tokens at rest. Losing it makes stored tokens
    # unreadable, so people would have to connect Google again.
    token_encryption_key: SecretStr

    @field_validator("token_encryption_key")
    @classmethod
    def check_fernet_key(cls, value: SecretStr) -> SecretStr:
        try:
            Fernet(value.get_secret_value())
        except ValueError:
            raise ValueError(
                "must be a Fernet key: 32 url-safe base64-encoded bytes (see .env.example)"
            ) from None
        return value

    @model_validator(mode="after")
    def require_google_in_production(self) -> Self:
        if self.is_production and not self.google_sign_in_enabled:
            raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in production")
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def google_sign_in_enabled(self) -> bool:
        return self.google_client_id is not None and self.google_client_secret is not None


@lru_cache
def get_settings() -> Settings:
    return Settings()
