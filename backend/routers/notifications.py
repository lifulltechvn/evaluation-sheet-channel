"""BFF Layer: Notification endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_permissions
from schemas.requests import SendResultsRequest
from services import notification_service

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])


@router.post("/send-results")
def send_results(req: SendResultsRequest, db: Session = Depends(get_db), _user: dict = Depends(require_permissions("manage_all"))):
    """Only CEO/HR can send result emails."""
    results = notification_service.send_results_to_employees(
        db=db,
        period=req.period,
        employee_ids=req.employee_ids,
    )
    return {"status": "success", "results": results}
