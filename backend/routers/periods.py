"""BFF Layer: Evaluation periods endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import EvaluationPeriod

router = APIRouter(prefix="/v1/periods", tags=["periods"])


@router.get("")
def list_periods(db: Session = Depends(get_db), _user: dict = Depends(get_current_user)):
    periods = db.query(EvaluationPeriod).order_by(EvaluationPeriod.start_date.desc()).all()
    return [{"id": p.id, "name": p.name, "start_date": str(p.start_date), "end_date": str(p.end_date), "status": p.status} for p in periods]
