"""Core business logic for notifications."""

from sqlalchemy.orm import Session

from repositories import employee_repository


def send_results_to_employees(db: Session, period: str, employee_ids: list[str]) -> list[dict]:
    """Send result notifications to a list of employees."""
    results = []
    for eid in employee_ids:
        emp = employee_repository.get_by_id(db, eid)
        if emp:
            results.append({
                "employee_id": eid,
                "email": emp["email"],
                "sent": True,
                "message": f"[MOCK] Result email sent to {emp['email']}",
            })
        else:
            results.append({
                "employee_id": eid,
                "sent": False,
                "error": "Employee not found",
            })
    return results
