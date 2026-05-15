"""BFF Layer: Sheets endpoints — aggregate and transform for frontend."""

import json
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, require_permissions, require_any_permission
from models import User, Template, EvaluationPeriod, Evaluation, Team
from schemas.requests import BatchSendRequest, MigrateRequest
from services import sheet_service
from services.google_drive_service import copy_template_to_folder, list_files_in_folder, get_or_create_folder
from repositories import sheet_repository

router = APIRouter(prefix="/v1/sheets", tags=["sheets"])


class GenerateByPeriodRequest:
    pass


@router.post("/generate")
def generate_sheets(period_id: str, db: Session = Depends(get_db), _user: dict = Depends(require_permissions("manage_all"))):
    """
    Generate evaluation sheets for ALL employees who have a template_id.
    Copies the template spreadsheet into the period's Drive folder.
    File name format: 【】Full_name Evaluation Sheet period_name
    """
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == period_id).first()
    if not period:
        raise HTTPException(404, "Period not found")

    users = db.query(User).filter(User.template_id.isnot(None), User.status == "active").all()
    if not users:
        raise HTTPException(400, "No employees with template assigned")

    # Preload templates
    templates = {t.id: t for t in db.query(Template).all()}
    teams = {t.id: t for t in db.query(Team).all()}
    folder_cache = {}

    def get_team_folder(team_id: str) -> str:
        if team_id in folder_cache:
            return folder_cache[team_id]
        team = teams.get(team_id)
        if not team:
            return period.folder_id
        if team.parent_id:
            parent_folder = get_team_folder(team.parent_id)
            folder_id = get_or_create_folder(parent_folder, team.name)
        else:
            folder_id = get_or_create_folder(period.folder_id, team.name)
        folder_cache[team_id] = folder_id
        return folder_id

    created = []
    for user in users:
        # Skip if evaluation already exists for this user+period
        existing = db.query(Evaluation).filter(
            Evaluation.employee_id == user.id,
            Evaluation.period_id == period_id,
            Evaluation.deleted_at.is_(None),
        ).first()
        if existing:
            continue

        template = templates.get(user.template_id)
        if not template:
            continue

        file_name = f"【】{user.full_name} Evaluation Sheet {period.name}"
        target_folder = get_team_folder(user.team_id) if user.team_id else period.folder_id

        result = copy_template_to_folder(
            template_file_id=template.google_file_id,
            folder_id=target_folder,
            file_name=file_name,
        )

        evaluation = Evaluation(
            id=f"EVAL_{user.id}_{period_id}",
            employee_id=user.id,
            template_id=user.template_id,
            period_id=period_id,
            spreadsheet_id=result["spreadsheet_id"],
            spreadsheet_url=result["spreadsheet_url"],
            status="Self_Evaluating",
            current_handler_id=user.id,
        )
        db.add(evaluation)
        created.append({
            "employee_id": user.id,
            "full_name": user.full_name,
            "spreadsheet_url": result["spreadsheet_url"],
        })

    db.commit()
    return {"status": "success", "sheets_created": len(created), "sheets": created}


@router.post("/generate-stream")
def generate_sheets_stream(period_id: str, db: Session = Depends(get_db), _user: dict = Depends(require_permissions("manage_all"))):
    """SSE endpoint: streams progress events while generating sheets."""
    period = db.query(EvaluationPeriod).filter(EvaluationPeriod.id == period_id).first()
    if not period:
        raise HTTPException(404, "Period not found")

    users = db.query(User).filter(User.template_id.isnot(None), User.status == "active").all()
    if not users:
        raise HTTPException(400, "No employees with template assigned")

    templates = {t.id: t for t in db.query(Template).all()}
    teams = {t.id: t for t in db.query(Team).all()}
    total = len(users)

    def event_stream():
        # Cache for resolved folder IDs: team_id -> folder_id
        folder_cache = {}

        def get_team_folder(team_id: str) -> str:
            """Resolve folder for a team: Period / Unit / Group"""
            if team_id in folder_cache:
                return folder_cache[team_id]
            team = teams.get(team_id)
            if not team:
                return period.folder_id
            if team.parent_id:
                # GROUP → create inside parent UNIT folder
                parent_folder = get_team_folder(team.parent_id)
                folder_id = get_or_create_folder(parent_folder, team.name)
            else:
                # UNIT → create inside period folder
                folder_id = get_or_create_folder(period.folder_id, team.name)
            folder_cache[team_id] = folder_id
            return folder_id

        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"
        created = 0
        skipped = 0
        for i, user in enumerate(users, 1):
            template = templates.get(user.template_id)
            if not template:
                continue

            file_name = f"【】{user.full_name} Evaluation Sheet {period.name}"

            # Check DB
            existing_eval = db.query(Evaluation).filter(
                Evaluation.employee_id == user.id,
                Evaluation.period_id == period_id,
                Evaluation.deleted_at.is_(None),
            ).first()
            if existing_eval:
                skipped += 1
                yield f"data: {json.dumps({'type': 'skipped', 'current': i, 'total': total, 'name': user.full_name, 'reason': 'db_exists'})}\n\n"
                continue

            # Resolve target folder based on user's team
            target_folder = get_team_folder(user.team_id) if user.team_id else period.folder_id

            # Copy template to team folder
            result = copy_template_to_folder(
                template_file_id=template.google_file_id,
                folder_id=target_folder,
                file_name=file_name,
            )
            evaluation = Evaluation(
                id=f"EVAL_{user.id}_{period_id}",
                employee_id=user.id,
                template_id=user.template_id,
                period_id=period_id,
                spreadsheet_id=result["spreadsheet_id"],
                spreadsheet_url=result["spreadsheet_url"],
                status="Self_Evaluating",
                current_handler_id=user.id,
            )
            db.add(evaluation)
            created += 1
            yield f"data: {json.dumps({'type': 'progress', 'current': i, 'total': total, 'name': user.full_name})}\n\n"
        db.commit()
        yield f"data: {json.dumps({'type': 'done', 'sheets_created': created, 'skipped': skipped})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("")
def list_sheets(
    period: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_any_permission("view_all", "view_unit", "view_group")),
):
    """CEO/HR/Unit Manager/Group Leader can list sheets."""
    query = db.query(Evaluation, User.full_name, Template.name.label("template_name")).join(
        User, Evaluation.employee_id == User.id
    ).join(Template, Evaluation.template_id == Template.id).filter(Evaluation.deleted_at.is_(None))
    if period:
        query = query.filter(Evaluation.period_id == period)
    if status:
        query = query.filter(Evaluation.status == status)
    rows = query.all()
    sheets = [
        {
            "sheet_id": ev.id,
            "employee_name": full_name,
            "position": template_name,
            "grade": ev.rank or "—",
            "period": ev.period_id,
            "status": ev.status,
            "spreadsheet_url": ev.spreadsheet_url,
        }
        for ev, full_name, template_name in rows
    ]
    return {"sheets": sheets, "total": len(sheets)}


@router.get("/{sheet_id}")
def get_sheet(sheet_id: str, _user: dict = Depends(get_current_user)):
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    return sheet


@router.post("/{sheet_id}/send")
def send_sheet(sheet_id: str, _user: dict = Depends(require_permissions("manage_all"))):
    """Only CEO/HR can send sheets."""
    sheet = sheet_repository.get_by_id(sheet_id)
    if sheet is None:
        raise HTTPException(404, "Sheet not found")
    sheet_repository.update_status(sheet_id, "sent")
    return {"status": "success", "message": f"[MOCK] Email sent to {sheet['email']}"}


@router.post("/batch-send")
def batch_send(req: BatchSendRequest, _user: dict = Depends(require_permissions("manage_all"))):
    """Only CEO/HR can batch send."""
    results = []
    for sid in req.sheet_ids:
        if sheet_repository.get_by_id(sid):
            sheet_repository.update_status(sid, "sent")
            results.append({"sheet_id": sid, "sent": True})
        else:
            results.append({"sheet_id": sid, "sent": False, "error": "Not found"})
    return {"status": "success", "results": results}


@router.post("/{sheet_id}/validate")
def validate_sheet(sheet_id: str, _user: dict = Depends(require_any_permission("manage_all", "review_evaluations", "approve_evaluations"))):
    """CEO/HR/Unit Manager/Group Leader can validate."""
    result = sheet_service.validate_sheet(sheet_id)
    if result is None:
        raise HTTPException(404, "Sheet not found")
    return result


@router.post("/batch-validate")
def batch_validate(req: BatchSendRequest, _user: dict = Depends(require_any_permission("manage_all", "review_evaluations", "approve_evaluations"))):
    """CEO/HR/Unit Manager/Group Leader can batch validate."""
    results = []
    for sid in req.sheet_ids:
        result = sheet_service.validate_sheet(sid)
        if result is None:
            results.append({"sheet_id": sid, "status": "error", "errors": [{"field": "sheet", "error": "Not found"}], "warnings": []})
        else:
            results.append(result)
    return {"results": results}


@router.post("/migrate")
def migrate_sheets(req: MigrateRequest, _user: dict = Depends(require_permissions("manage_all"))):
    """Only CEO/HR can migrate sheets."""
    migrated = sheet_service.migrate_sheets(
        from_period=req.from_period,
        to_period=req.to_period,
        employee_updates=req.employee_updates,
    )
    return {"status": "success", "migrated": len(migrated), "sheets": migrated}
