"""BFF Layer: Notification endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas.requests import SendResultsRequest
from services import notification_service

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])


@router.post("/send-results")
def send_results(req: SendResultsRequest, db: Session = Depends(get_db)):
    results = notification_service.send_results_to_employees(
        db=db,
        period=req.period,
        employee_ids=req.employee_ids,
    )
    return {"status": "success", "results": results}
