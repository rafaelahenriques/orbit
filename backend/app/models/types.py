from sqlalchemy import Text
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from app.encryption import decrypt, encrypt


class EncryptedText(TypeDecorator[str]):
    """Text that is encrypted before it is written and decrypted when it is read.

    Code works with plaintext, while the database only ever holds ciphertext.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:
        return None if value is None else encrypt(value)

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        return None if value is None else decrypt(value)
