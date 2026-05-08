"""Data access layer for employees — queries real database."""

from sqlalchemy.orm import Session

from models import User, Role, Team, Evaluation


def get_by_id(db: Session, employee_id: str) -> dict | None:
    """Get a single employee by ID."""
    row = (
        db.query(User, Role.name.label("role_name"), Team.name.label("team_name"))
        .join(Role, User.role_id == Role.id)
        .outerjoin(Team, User.team_id == Team.id)
        .filter(User.id == employee_id, User.deleted_at.is_(None))
        .first()
    )
    if row is None:
        return None
    u, role_name, team_name = row
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": role_name,
        "team": team_name,
        "status": u.status,
    }


def get_all(db: Session) -> list[dict]:
    """Get all active employees."""
    rows = (
        db.query(User, Role.name.label("role_name"), Team.name.label("team_name"))
        .join(Role, User.role_id == Role.id)
        .outerjoin(Team, User.team_id == Team.id)
        .filter(User.deleted_at.is_(None))
        .order_by(User.full_name)
        .all()
    )
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": role_name,
            "team": team_name,
            "status": u.status,
        }
        for u, role_name, team_name in rows
    ]


def exists(db: Session, employee_id: str) -> bool:
    """Check if an employee exists."""
    return db.query(User).filter(User.id == employee_id, User.deleted_at.is_(None)).first() is not None
