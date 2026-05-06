"""BFF Layer: Sheets endpoints — aggregate and transform for frontend."""

from fastapi import APIRouter, HTTPException

from schemas.requests import GenerateRequest, BatchSendRequest, MigrateRequest
from services import sheet_service
from services.scoring_service import get_scoring
from repositories import sheet_repository

import uuid
from datetime import datetime

router = APIRouter(prefix="/v1/sheets", tags=["sheets"])


@router.post("/generate")
def generate_sheets(req: GenerateRequest):
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
def list_sheets(period: str | None = None, status: str | None = None, position: str | None = None):
    results = sheet_repository.get_all(period=period, status=status, position=position)
    return {"sheets": results, "total": len(results)}


@router.get("/{sheet_id}")
def get_sheet(sheet_id: str):
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    return sheet


@router.post("/{sheet_id}/send")
def send_sheet(sheet_id: str):
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    sheet_repository.update_status(sheet_id, "sent")
    return {"status": "success", "message": f"[MOCK] Email sent to {sheet['email']}"}


@router.post("/batch-send")
def batch_send(req: BatchSendRequest):
    results = []
    for sid in req.sheet_ids:
        if sheet_repository.get_by_id(sid):
            sheet_repository.update_status(sid, "sent")
            results.append({"sheet_id": sid, "sent": True})
        else:
            results.append({"sheet_id": sid, "sent": False, "error": "Not found"})
    return {"status": "success", "results": results}


@router.post("/{sheet_id}/validate")
def validate_sheet(sheet_id: str):
    result = sheet_service.validate_sheet(sheet_id)
    if result is None:
        raise HTTPException(404, "Sheet not found")
    return result


@router.post("/batch-validate")
def batch_validate(req: BatchSendRequest):
    results = []
    for sid in req.sheet_ids:
        result = sheet_service.validate_sheet(sid)
        if result is None:
            results.append({"sheet_id": sid, "status": "error", "errors": [{"field": "sheet", "error": "Not found"}], "warnings": []})
        else:
            results.append(result)
    return {"results": results}


@router.post("/migrate")
def migrate_sheets(req: MigrateRequest):
    source_sheets = sheet_repository.get_by_period(req.from_period)
    updates_map = {u["employee_id"]: u for u in (req.employee_updates or [])}
    migrated = []

    for src in source_sheets:
        new_grade = updates_map.get(src["employee_id"], {}).get("new_grade", src["grade"])
        new_scoring = get_scoring(src["position"], new_grade)
        sheet_id = f"SHEET-{req.to_period}-{uuid.uuid4().hex[:6].upper()}"
        sheet = {
            **src,
            "sheet_id": sheet_id,
            "period": req.to_period,
            "grade": new_grade,
            "status": "created",
            "scoring_criteria": new_scoring,
            "google_sheet_url": f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}",
            "created_at": datetime.now().isoformat(),
            "migrated_from": src["sheet_id"],
        }
        sheet_repository.save(sheet)
        migrated.append({
            "sheet_id": sheet_id,
            "employee_id": src["employee_id"],
            "old_grade": src["grade"],
            "new_grade": new_grade,
        })

    return {"status": "success", "migrated": len(migrated), "sheets": migrated}
