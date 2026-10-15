from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.sessions import SESSION_COOKIE, read_session_cookie
from app.config import Settings, get_settings
from app.db import get_db
from app.models import User


def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """FastAPI dependency for routes that need a signed-in user. Responds 401 otherwise."""
    user_id = read_session_cookie(request.cookies.get(SESSION_COOKIE), settings)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
