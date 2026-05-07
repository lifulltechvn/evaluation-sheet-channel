"""BFF Layer: Employee history endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from services import employee_service

router = APIRouter(prefix="/v1/employees", tags=["history"])


@router.get("/{employee_id}/history")
def get_history(employee_id: str, db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
    result = employee_service.get_employee_history(db, employee_id)
    if result is None:
        raise HTTPException(404, "Employee not found")
    return result
