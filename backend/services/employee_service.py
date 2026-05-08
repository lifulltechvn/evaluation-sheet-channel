"""Core business logic for employees."""

from sqlalchemy.orm import Session

from models import Evaluation
from repositories import employee_repository


def get_employees_from_db(db: Session) -> dict:
    """Fetch all active employees."""
    employees = employee_repository.get_all(db)
    return {"employees": employees, "total": len(employees)}


def get_employee_history(db: Session, employee_id: str) -> dict | None:
    """Get evaluation history for an employee from real DB."""
    if not employee_repository.exists(db, employee_id):
        return None

    evaluations = (
        db.query(Evaluation)
        .filter(Evaluation.employee_id == employee_id, Evaluation.deleted_at.is_(None))
        .order_by(Evaluation.created_at.desc())
        .all()
    )

    history = [
        {
            "period_id": ev.period_id,
            "status": ev.status,
            "final_score": ev.final_score,
            "rank": ev.rank,
            "spreadsheet_url": ev.spreadsheet_url,
        }
        for ev in evaluations
    ]
    return {"employee_id": employee_id, "history": history}
