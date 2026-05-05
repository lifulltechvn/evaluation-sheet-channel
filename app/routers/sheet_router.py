from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.schemas.sheet_schema import BatchSendRequest, GenerateRequest, MigrateRequest
from app.services.sheet_service import sheet_service

router = APIRouter(prefix="/v1/sheets", tags=["Sheets"])


@router.post("/generate")
async def generate_sheets(req: GenerateRequest, db: AsyncSession = Depends(get_db)):
    employees = [emp.model_dump() for emp in req.employees]
    return await sheet_service.generate(db, req.period, employees)


@router.get("")
async def list_sheets(
    period: str | None = None,
    status: str | None = None,
    position: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await sheet_service.list_sheets(db, period, status, position)


@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str, db: AsyncSession = Depends(get_db)):
    return await sheet_service.get_sheet(db, sheet_id)


@router.post("/{sheet_id}/send")
async def send_sheet(sheet_id: str, db: AsyncSession = Depends(get_db)):
    return await sheet_service.send_sheet(db, sheet_id)


@router.post("/batch-send")
async def batch_send(req: BatchSendRequest, db: AsyncSession = Depends(get_db)):
    return await sheet_service.batch_send(db, req.sheet_ids)


@router.post("/{sheet_id}/validate")
async def validate_sheet(sheet_id: str, db: AsyncSession = Depends(get_db)):
    return await sheet_service.validate_sheet(db, sheet_id)


@router.post("/batch-validate")
async def batch_validate(req: BatchSendRequest, db: AsyncSession = Depends(get_db)):
    return await sheet_service.batch_validate(db, req.sheet_ids)


@router.post("/migrate")
async def migrate_sheets(req: MigrateRequest, db: AsyncSession = Depends(get_db)):
    return await sheet_service.migrate(db, req.from_period, req.to_period, req.employee_updates)
