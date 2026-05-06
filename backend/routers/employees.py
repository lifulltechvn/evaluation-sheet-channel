"""BFF Layer: Employees endpoints — format employee data for frontend."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services import employee_service

router = APIRouter(prefix="/v1/employees", tags=["employees"])


@router.get("")
def list_employees(db: Session = Depends(get_db)):
    return employee_service.get_employees_from_db(db)
