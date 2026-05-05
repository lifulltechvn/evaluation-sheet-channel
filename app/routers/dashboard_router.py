from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.repositories.sheet_repository import sheet_repository

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


@router.get("/status")
async def dashboard_status(db: AsyncSession = Depends(get_db)):
    all_sheets = await sheet_repository.get_all(db)
    counts: dict[str, int] = {}
    for s in all_sheets:
        counts[s.status] = counts.get(s.status, 0) + 1
    return {"total_sheets": len(all_sheets), "by_status": counts}
