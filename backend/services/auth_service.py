"""Core business logic for authentication."""

import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from repositories import auth_repository

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "120"))


def authenticate_user(db: Session, email: str, password: str) -> dict | None:
    """Verify email/password. Returns user info or None."""
    user_id = auth_repository.verify_credentials(db, email, password)
    if user_id is None:
        return None

    return auth_repository.get_user_with_role(db, user_id)


def create_access_token(user_data: dict) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "permissions": user_data["permissions"],
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
