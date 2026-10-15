from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import google
from app.auth.google import GoogleProfile, GoogleTokens
from app.models import OAuthAccount, User


def save_google_sign_in(db: Session, profile: GoogleProfile, tokens: GoogleTokens) -> User:
    """Finds or creates the user for a Google account, and stores its latest tokens."""
    account = db.scalar(
        select(OAuthAccount).where(
            OAuthAccount.provider == google.PROVIDER,
            OAuthAccount.provider_account_id == profile.sub,
        )
    )
    if account is None:
        user = db.scalar(select(User).where(User.email == profile.email))
        if user is None:
            user = User(email=profile.email)
            db.add(user)
        account = OAuthAccount(user=user, provider=google.PROVIDER, provider_account_id=profile.sub)
        db.add(account)

    account.user.email = profile.email
    account.user.name = profile.name
    account.scopes = tokens.scope
    account.access_token = tokens.access_token
    account.access_token_expires_at = datetime.now(UTC) + timedelta(seconds=tokens.expires_in)
    # Google leaves the refresh token out when the user already gave consent, so keep
    # the one we have rather than losing offline access.
    if tokens.refresh_token is not None:
        account.refresh_token = tokens.refresh_token

    db.commit()
    return account.user


def find_google_account(db: Session, user: User) -> OAuthAccount | None:
    return db.scalar(
        select(OAuthAccount).where(
            OAuthAccount.user_id == user.id, OAuthAccount.provider == google.PROVIDER
        )
    )


def can_sync_google(account: OAuthAccount | None) -> bool:
    """Whether Orbit can read the user's Gmail and Calendar in the background."""
    return (
        account is not None
        and account.refresh_token is not None
        and google.SYNC_SCOPES.issubset(account.granted_scopes)
    )
