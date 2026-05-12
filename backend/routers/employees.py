"""BFF Layer: Employee endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_any_permission
from services import employee_service

router = APIRouter(prefix="/v1/employees", tags=["employees"])


@router.get("")
def list_employees(db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
    """List all employees."""
    return employee_service.get_employees_from_db(db)


@router.get("/me/history")
def get_my_history(db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
    """Get evaluation history for the currently logged-in user."""
    result = employee_service.get_employee_history(db, _user["sub"])
    if result is None:
        raise HTTPException(404, "No history found")
    return result


@router.get("/{employee_id}/history")
def get_history(employee_id: str, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
    """Users with view_all/view_unit can view anyone. Others only view their own."""
    perms = _user.get("permissions", {})
    can_view_others = perms.get("view_all") or perms.get("view_unit") or perms.get("all")

    if not can_view_others and _user["sub"] != employee_id:
        raise HTTPException(403, "You can only view your own history")

    result = employee_service.get_employee_history(db, employee_id)
    if result is None:
        raise HTTPException(404, "Employee not found")
    return result
