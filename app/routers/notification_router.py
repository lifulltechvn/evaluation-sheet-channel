from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.schemas.notification_schema import SendResultsRequest
from app.services.notification_service import notification_service

router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


@router.post("/send-results")
async def send_results(req: SendResultsRequest, db: AsyncSession = Depends(get_db)):
    return await notification_service.send_results(db, req.period, req.employee_ids)
