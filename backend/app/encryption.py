"""Encryption for sensitive values stored in the database, such as OAuth tokens.

Fernet is authenticated encryption, so a tampered or wrongly keyed value fails to
decrypt instead of returning garbage.
"""

from cryptography.fernet import Fernet

from app.config import get_settings


def _fernet() -> Fernet:
    return Fernet(get_settings().token_encryption_key.get_secret_value())


def encrypt(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Raises cryptography.fernet.InvalidToken if the value was not encrypted with our key."""
    return _fernet().decrypt(ciphertext.encode()).decode()
