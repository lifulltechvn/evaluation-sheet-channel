from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.employee_repository import employee_repository


class NotificationService:
    async def send_results(self, db: AsyncSession, period: str, employee_ids: list[str]) -> dict:
        sent = []
        for eid in employee_ids:
            emp = await employee_repository.get_by_id(db, eid)
            if emp:
                sent.append({
                    "employee_id": eid,
                    "email": emp.email,
                    "sent": True,
                    "message": f"[MOCK] Result email sent to {emp.email}",
                })
            else:
                sent.append({
                    "employee_id": eid,
                    "sent": False,
                    "error": "Employee not found",
                })
        return {"status": "success", "results": sent}


notification_service = NotificationService()
