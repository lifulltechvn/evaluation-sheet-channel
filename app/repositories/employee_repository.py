from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.history import EvaluationHistory


class EmployeeRepository:
    async def get_all(self, db: AsyncSession) -> list[Employee]:
        result = await db.execute(select(Employee))
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, employee_id: str) -> Employee | None:
        return await db.get(Employee, employee_id)

    async def exists(self, db: AsyncSession, employee_id: str) -> bool:
        emp = await db.get(Employee, employee_id)
        return emp is not None

    async def get_history(self, db: AsyncSession, employee_id: str) -> list[EvaluationHistory]:
        result = await db.execute(
            select(EvaluationHistory)
            .where(EvaluationHistory.employee_id == employee_id)
            .order_by(EvaluationHistory.period.desc())
        )
        return list(result.scalars().all())


employee_repository = EmployeeRepository()
