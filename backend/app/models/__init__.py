# Import every model here so Alembic sees the full schema through Base.metadata.
from app.models.base import Base
from app.models.oauth_account import OAuthAccount
from app.models.user import User

__all__ = ["Base", "OAuthAccount", "User"]
