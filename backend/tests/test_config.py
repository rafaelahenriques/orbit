import pytest
from pydantic import ValidationError

from app.config import Settings


def test_secrets_have_no_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SESSION_SECRET")
    monkeypatch.delenv("TOKEN_ENCRYPTION_KEY")

    with pytest.raises(ValidationError) as error:
        Settings()

    missing = {str(detail["loc"][0]) for detail in error.value.errors()}
    assert missing == {"session_secret", "token_encryption_key"}


def test_empty_values_count_as_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # A .env copied from .env.example has `SESSION_SECRET=` with nothing after it.
    monkeypatch.setenv("SESSION_SECRET", "")

    with pytest.raises(ValidationError, match="session_secret"):
        Settings()


def test_google_sign_in_is_optional_outside_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET")

    assert Settings().google_sign_in_enabled is False


def test_production_requires_google_sign_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_CLIENT_ID")
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET")

    with pytest.raises(ValidationError, match="must be set in production"):
        Settings(environment="production")


def test_session_secret_must_be_long() -> None:
    with pytest.raises(ValidationError, match="session_secret"):
        Settings(session_secret="too-short")


def test_token_encryption_key_must_be_a_fernet_key() -> None:
    with pytest.raises(ValidationError, match="must be a Fernet key"):
        Settings(token_encryption_key="not-a-fernet-key")


def test_errors_do_not_reveal_secret_values() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(token_encryption_key="my-real-key-with-a-typo")

    assert "my-real-key-with-a-typo" not in str(error.value)
