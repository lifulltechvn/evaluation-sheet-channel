"""Core business logic for employees."""

from sqlalchemy.orm import Session

from models import Evaluation, EvaluationPeriod
from repositories import employee_repository


def get_employees_from_db(db: Session) -> dict:
    """Fetch all active employees."""
    employees = employee_repository.get_all(db)
    return {"employees": employees, "total": len(employees)}


def get_employee_history(db: Session, employee_id: str) -> dict | None:
    """Get evaluation history for an employee from real DB."""
    employee = employee_repository.get_by_id(db, employee_id)
    if employee is None:
        return None

    evaluations = (
        db.query(Evaluation, EvaluationPeriod.name.label("period_name"))
        .join(EvaluationPeriod, Evaluation.period_id == EvaluationPeriod.id)
        .filter(Evaluation.employee_id == employee_id, Evaluation.deleted_at.is_(None))
        .order_by(EvaluationPeriod.name.desc())
        .all()
    )

    history = [
        {
            "period_id": ev.period_id,
            "period_name": period_name,
            "status": ev.status,
            "final_score": ev.final_score,
            "rank": ev.rank,
            "spreadsheet_url": ev.spreadsheet_url,
        }
        for ev, period_name in evaluations
    ]
    return {"employee_id": employee_id, "employee_name": employee["full_name"], "history": history}
