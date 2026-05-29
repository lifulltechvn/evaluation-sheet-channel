"""Core business logic for notifications."""

from sqlalchemy.orm import Session

from repositories import employee_repository, sheet_repository
from services import ai_service


def send_results_to_employees(db: Session, period: str, employee_ids: list[str]) -> list[dict]:
    """Send result notifications with AI feedback to a list of employees."""
    results = []
    for eid in employee_ids:
        emp = employee_repository.get_by_id(db, eid)
        if not emp:
            results.append({"employee_id": eid, "sent": False, "error": "Employee not found"})
            continue

        # Get the latest sheet for this employee in the given period
        sheets = sheet_repository.get_all(period=period)
        emp_sheet = next((s for s in sheets if s["employee_id"] == eid), None)

        feedback_data = emp_sheet.get("ai_feedback") if emp_sheet else None
        if not feedback_data and emp_sheet:
            # Generate on-the-fly if not already cached
            all_sheets = sheet_repository.get_all()
            previous = next(
                (s for s in sorted(all_sheets, key=lambda s: s.get("created_at", ""), reverse=True)
                 if s["employee_id"] == eid and s["sheet_id"] != emp_sheet["sheet_id"]),
                None,
            )
            feedback_data = ai_service.generate_feedback_and_recommend(emp_sheet, previous)

        results.append({
            "employee_id": eid,
            "email": emp["email"],
            "sent": True,
            "message": f"[MOCK] Result email sent to {emp['email']}",
            "ai_feedback": feedback_data,
        })
    return results
