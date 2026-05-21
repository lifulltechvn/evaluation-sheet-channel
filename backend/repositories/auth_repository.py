"""Data access layer for authentication."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from models import User, Role


def verify_credentials(db: Session, email: str, password: str) -> str | None:
    """Verify email/password using pgcrypto crypt(). Returns user_id or None."""
    result = db.execute(
        text("SELECT id FROM users WHERE email = :email AND password = crypt(:password, password) AND deleted_at IS NULL"),
        {"email": email, "password": password},
    ).fetchone()

    if result is None:
        return None
    return result[0]


def get_user_with_role(db: Session, user_id: str) -> dict | None:
    """Get user info with role name and permissions."""
    row = (
        db.query(User, Role.name.label("role_name"), Role.permissions.label("permissions"))
        .join(Role, User.role_id == Role.id)
        .filter(User.id == user_id)
        .first()
    )
    if row is None:
        return None

    u, role_name, permissions = row
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "role": role_name,
        "team_id": u.team_id,
        "permissions": permissions,
    }
