from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.repositories.employee_repository import employee_repository
from app.repositories.sheet_repository import sheet_repository


class EmployeeService:
    async def list_employees(self, db: AsyncSession) -> dict:
        employees = await employee_repository.get_all(db)
        all_sheets = await sheet_repository.get_all(db)

        result = []
        for emp in employees:
            sheets = [s for s in all_sheets if s.employee_id == emp.employee_id]
            latest = max(sheets, key=lambda x: x.created_at) if sheets else None
            result.append({
                "employee_id": emp.employee_id,
                "name": emp.name,
                "email": emp.email,
                "position": emp.position,
                "grade": emp.grade,
                "latest_sheet_status": latest.status if latest else "none",
                "latest_period": latest.period if latest else None,
            })
        return {"employees": result, "total": len(result)}

    async def get_history(self, db: AsyncSession, employee_id: str) -> dict:
        if not await employee_repository.exists(db, employee_id):
            raise NotFoundException("Employee not found")
        history = await employee_repository.get_history(db, employee_id)
        return {
            "employee_id": employee_id,
            "history": [
                {
                    "period": h.period,
                    "grade": h.grade,
                    "position": h.position,
                    "total_score": h.total_score,
                    "google_sheet_url": h.google_sheet_url,
                }
                for h in history
            ],
        }


employee_service = EmployeeService()
