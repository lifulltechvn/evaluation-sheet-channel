"""BFF Layer: Dashboard endpoints — aggregate data from multiple services."""

from fastapi import APIRouter

from repositories import sheet_repository

router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/status")
def dashboard_status():
    all_sheets = sheet_repository.get_all()
    counts: dict[str, int] = {}
    for s in all_sheets:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    return {"total_sheets": len(all_sheets), "by_status": counts}
