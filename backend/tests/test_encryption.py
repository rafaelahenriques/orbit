from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.encryption import decrypt, encrypt
from app.models import OAuthAccount, User


@pytest.fixture
def different_key(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("TOKEN_ENCRYPTION_KEY", Fernet.generate_key().decode())
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_encrypted_value_decrypts_to_the_original() -> None:
    assert decrypt(encrypt("refresh-token")) == "refresh-token"


def test_ciphertext_does_not_reveal_the_value() -> None:
    first = encrypt("refresh-token")
    second = encrypt("refresh-token")

    assert "refresh-token" not in first
    # A random IV per value means equal tokens cannot be spotted in the database.
    assert first != second


def test_value_cannot_be_decrypted_with_a_different_key(different_key: None) -> None:
    ciphertext = Fernet(Fernet.generate_key()).encrypt(b"refresh-token").decode()

    with pytest.raises(InvalidToken):
        decrypt(ciphertext)


def test_tampered_ciphertext_is_rejected() -> None:
    ciphertext = encrypt("refresh-token")
    tampered = ciphertext[:-2] + ("A" if ciphertext[-2] != "A" else "B") + ciphertext[-1]

    with pytest.raises(InvalidToken):
        decrypt(tampered)


def test_oauth_tokens_are_stored_encrypted(db: Session) -> None:
    account = OAuthAccount(
        user=User(email="ada@example.com"),
        provider="google",
        provider_account_id="google-user-1",
        scopes="openid",
        access_token="access-token",
        access_token_expires_at=datetime.now(UTC),
        refresh_token="refresh-token",
    )
    db.add(account)
    db.commit()

    stored = db.execute(text("SELECT refresh_token FROM oauth_accounts")).scalar_one()
    assert stored != "refresh-token"
    assert decrypt(stored) == "refresh-token"

    db.expire_all()
    assert account.refresh_token == "refresh-token"
