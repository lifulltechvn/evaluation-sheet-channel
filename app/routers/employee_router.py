from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.services.employee_service import employee_service

router = APIRouter(prefix="/v1/employees", tags=["Employees"])


@router.get("")
async def list_employees(db: AsyncSession = Depends(get_db)):
    return await employee_service.list_employees(db)


@router.get("/{employee_id}/history")
async def get_history(employee_id: str, db: AsyncSession = Depends(get_db)):
    return await employee_service.get_history(db, employee_id)
