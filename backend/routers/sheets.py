"""BFF Layer: Sheets endpoints — aggregate and transform for frontend."""

from fastapi import APIRouter, HTTPException, Depends

from dependencies import get_current_user
from schemas.requests import GenerateRequest, BatchSendRequest, MigrateRequest
from services import sheet_service
from repositories import sheet_repository

router = APIRouter(prefix="/v1/sheets", tags=["sheets"])


@router.post("/generate")
def generate_sheets(req: GenerateRequest, _user: dict = Depends(get_current_user)):
    created = []
    for emp in req.employees:
        sheet = sheet_service.create_sheet(
            employee_id=emp.employee_id,
            name=emp.name,
            email=emp.email,
            position=emp.position,
            grade=emp.grade,
            period=req.period,
        )
        created.append({
            "sheet_id": sheet["sheet_id"],
            "employee_id": emp.employee_id,
            "google_sheet_url": sheet["google_sheet_url"],
            "status": "created",
        })
    return {"status": "success", "sheets_created": len(created), "sheets": created}


@router.get("")
def list_sheets(
    period: str | None = None,
    status: str | None = None,
    position: str | None = None,
    _user: dict = Depends(get_current_user),
):
    results = sheet_repository.get_all(period=period, status=status, position=position)
    return {"sheets": results, "total": len(results)}


@router.get("/{sheet_id}")
def get_sheet(sheet_id: str, _user: dict = Depends(get_current_user)):
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    return sheet


@router.post("/{sheet_id}/send")
def send_sheet(sheet_id: str, _user: dict = Depends(get_current_user)):
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    sheet_repository.update_status(sheet_id, "sent")
    return {"status": "success", "message": f"[MOCK] Email sent to {sheet['email']}"}


@router.post("/batch-send")
def batch_send(req: BatchSendRequest, _user: dict = Depends(get_current_user)):
    results = []
    for sid in req.sheet_ids:
        if sheet_repository.get_by_id(sid):
            sheet_repository.update_status(sid, "sent")
            results.append({"sheet_id": sid, "sent": True})
        else:
            results.append({"sheet_id": sid, "sent": False, "error": "Not found"})
    return {"status": "success", "results": results}


@router.post("/{sheet_id}/validate")
def validate_sheet(sheet_id: str, _user: dict = Depends(get_current_user)):
    result = sheet_service.validate_sheet(sheet_id)
    if result is None:
        raise HTTPException(404, "Sheet not found")
    return result


@router.post("/batch-validate")
def batch_validate(req: BatchSendRequest, _user: dict = Depends(get_current_user)):
    results = []
    for sid in req.sheet_ids:
        result = sheet_service.validate_sheet(sid)
        if result is None:
            results.append({"sheet_id": sid, "status": "error", "errors": [{"field": "sheet", "error": "Not found"}], "warnings": []})
        else:
            results.append(result)
    return {"results": results}


@router.post("/migrate")
def migrate_sheets(req: MigrateRequest, _user: dict = Depends(get_current_user)):
    migrated = sheet_service.migrate_sheets(
        from_period=req.from_period,
        to_period=req.to_period,
        employee_updates=req.employee_updates,
    )
    return {"status": "success", "migrated": len(migrated), "sheets": migrated}
