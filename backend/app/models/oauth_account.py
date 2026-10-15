import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.types import EncryptedText

if TYPE_CHECKING:
    from app.models.user import User


class OAuthAccount(TimestampMixin, Base):
    """An external account a user signed in with, and the tokens Orbit holds for it."""

    __tablename__ = "oauth_accounts"
    __table_args__ = (UniqueConstraint("provider", "provider_account_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(32))
    # The provider's stable ID for the account. Unlike an email address, it never changes.
    provider_account_id: Mapped[str] = mapped_column(String(255))
    # Space-separated scopes the user granted. People can untick scopes on Google's
    # consent screen, so this can be fewer than Orbit asked for.
    scopes: Mapped[str] = mapped_column(Text)

    access_token: Mapped[str] = mapped_column(EncryptedText)
    access_token_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Lets the worker get new access tokens while the user is away. Google only issues
    # one when the user gives consent, so it can be missing.
    refresh_token: Mapped[str | None] = mapped_column(EncryptedText)

    user: Mapped[User] = relationship(back_populates="oauth_accounts")

    @property
    def granted_scopes(self) -> set[str]:
        return set(self.scopes.split())
