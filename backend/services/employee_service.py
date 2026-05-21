"""Core business logic for employees."""

from datetime import date

from sqlalchemy.orm import Session

from models import Evaluation, EvaluationPeriod
from repositories import employee_repository


def _enrich_with_current_sheet(db: Session, employees: list[dict]) -> list[dict]:
    """Add spreadsheet_url from the current active period to each employee."""
    active_period = db.query(EvaluationPeriod).filter(
        EvaluationPeriod.status == "active",
        EvaluationPeriod.start_date <= date.today(),
        EvaluationPeriod.end_date >= date.today(),
    ).first()
    if not active_period:
        for emp in employees:
            emp["spreadsheet_url"] = None
        return employees

    emp_ids = [e["id"] for e in employees]
    evals = (
        db.query(Evaluation.employee_id, Evaluation.spreadsheet_url)
        .filter(
            Evaluation.employee_id.in_(emp_ids),
            Evaluation.period_id == active_period.id,
            Evaluation.deleted_at.is_(None),
        )
        .all()
    )
    url_map = {ev.employee_id: ev.spreadsheet_url for ev in evals}
    for emp in employees:
        emp["spreadsheet_url"] = url_map.get(emp["id"])
    return employees


def get_employees_from_db(db: Session) -> dict:
    """Fetch all active employees."""
    employees = employee_repository.get_all(db)
    employees = _enrich_with_current_sheet(db, employees)
    return {"employees": employees, "total": len(employees)}


def get_employees_by_team(db: Session, team_id: str) -> dict:
    """Fetch active employees belonging to a specific team."""
    employees = employee_repository.get_by_team(db, team_id)
    employees = _enrich_with_current_sheet(db, employees)
    return {"employees": employees, "total": len(employees)}


def get_employees_by_unit(db: Session, unit_team_id: str) -> dict:
    """Fetch active employees belonging to a unit and its child groups."""
    employees = employee_repository.get_by_unit(db, unit_team_id)
    employees = _enrich_with_current_sheet(db, employees)
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
