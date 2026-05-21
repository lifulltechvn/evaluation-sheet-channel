"""BFF Layer: Dashboard endpoints — aggregate data from multiple services."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import require_any_permission
from models import Evaluation

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/status")
def dashboard_status(
    period_id: str | None = Query(None),
    db: Session = Depends(get_db),
    _user: dict = Depends(require_any_permission("view_all", "view_unit", "view_group")),
):
    """CEO/HR/Unit Manager/Group Leader can view dashboard."""
    query = db.query(Evaluation).filter(Evaluation.deleted_at.is_(None))
    if period_id:
        query = query.filter(Evaluation.period_id == period_id)
    evals = query.all()
    counts: dict[str, int] = {}
    for ev in evals:
        counts[ev.status] = counts.get(ev.status, 0) + 1
    return {"total_sheets": len(evals), "by_status": counts}
