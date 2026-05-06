"""Core business logic for evaluation sheets."""

import uuid
from datetime import datetime

from repositories import sheet_repository
from services.scoring_service import get_scoring


def create_sheet(employee_id: str, name: str, email: str, position: str, grade: str, period: str) -> dict:
    """Create a single evaluation sheet for an employee."""
    sheet_id = f"SHEET-{period}-{uuid.uuid4().hex[:6].upper()}"
    scoring = get_scoring(position, grade)
    sheet = {
        "sheet_id": sheet_id,
        "employee_id": employee_id,
        "employee_name": name,
        "email": email,
        "position": position,
        "grade": grade,
        "period": period,
        "status": "created",
        "scoring_criteria": scoring,
        "google_sheet_url": f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}",
        "created_at": datetime.now().isoformat(),
    }
    sheet_repository.save(sheet)
    return sheet


def validate_sheet(sheet_id: str) -> dict | None:
    """Validate a sheet and return validation result. Returns None if not found."""
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        return None

    errors: list[dict] = []
    warnings: list[dict] = []

    if sheet["status"] == "created":
        errors.append({"field": "self_evaluation", "error": "Self-evaluation not yet completed"})

    warnings.append({"field": "leadership_comment", "warning": "[MOCK AI] Comment appears too vague — consider adding specifics"})

    status = "fail" if errors else "pass"
    if status == "pass":
        sheet_repository.update_status(sheet_id, "validated")

    return {"sheet_id": sheet_id, "status": status, "errors": errors, "warnings": warnings}
