import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.models.sheet import Sheet
from app.repositories.sheet_repository import sheet_repository
from app.services.scoring_service import scoring_service


class SheetService:
    async def generate(self, db: AsyncSession, period: str, employees: list[dict]) -> dict:
        created = []
        for emp in employees:
            sheet_id = f"SHEET-{period}-{uuid.uuid4().hex[:6].upper()}"
            scoring = scoring_service.get_scoring(emp["position"], emp["grade"])
            sheet = Sheet(
                sheet_id=sheet_id,
                employee_id=emp["employee_id"],
                employee_name=emp["name"],
                email=emp["email"],
                position=emp["position"],
                grade=emp["grade"],
                period=period,
                status="created",
                scoring_criteria=scoring,
                google_sheet_url=f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}",
                migrated_from=None,
            )
            await sheet_repository.save(db, sheet)
            created.append({
                "sheet_id": sheet_id,
                "employee_id": emp["employee_id"],
                "google_sheet_url": sheet.google_sheet_url,
                "status": "created",
            })
        return {"status": "success", "sheets_created": len(created), "sheets": created}

    async def list_sheets(
        self,
        db: AsyncSession,
        period: str | None = None,
        status: str | None = None,
        position: str | None = None,
    ) -> dict:
        sheets = await sheet_repository.filter_by(db, period, status, position)
        results = [
            {
                "sheet_id": s.sheet_id,
                "employee_id": s.employee_id,
                "employee_name": s.employee_name,
                "email": s.email,
                "position": s.position,
                "grade": s.grade,
                "period": s.period,
                "status": s.status,
                "scoring_criteria": s.scoring_criteria,
                "google_sheet_url": s.google_sheet_url,
                "migrated_from": s.migrated_from,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sheets
        ]
        return {"sheets": results, "total": len(results)}

    async def get_sheet(self, db: AsyncSession, sheet_id: str) -> Sheet:
        sheet = await sheet_repository.get_by_id(db, sheet_id)
        if not sheet:
            raise NotFoundException("Sheet not found")
        return sheet

    def _sheet_to_dict(self, s: Sheet) -> dict:
        return {
            "sheet_id": s.sheet_id,
            "employee_id": s.employee_id,
            "employee_name": s.employee_name,
            "email": s.email,
            "position": s.position,
            "grade": s.grade,
            "period": s.period,
            "status": s.status,
            "scoring_criteria": s.scoring_criteria,
            "google_sheet_url": s.google_sheet_url,
            "migrated_from": s.migrated_from,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }

    async def send_sheet(self, db: AsyncSession, sheet_id: str) -> dict:
        sheet = await self.get_sheet(db, sheet_id)
        await sheet_repository.update_status(db, sheet_id, "sent")
        return {"status": "success", "message": f"[MOCK] Email sent to {sheet.email}"}

    async def batch_send(self, db: AsyncSession, sheet_ids: list[str]) -> dict:
        results = []
        for sid in sheet_ids:
            sheet = await sheet_repository.get_by_id(db, sid)
            if sheet:
                await sheet_repository.update_status(db, sid, "sent")
                results.append({"sheet_id": sid, "sent": True})
            else:
                results.append({"sheet_id": sid, "sent": False, "error": "Not found"})
        return {"status": "success", "results": results}

    async def validate_sheet(self, db: AsyncSession, sheet_id: str) -> dict:
        sheet = await self.get_sheet(db, sheet_id)
        errors: list[dict] = []
        warnings: list[dict] = []
        if sheet.status == "created":
            errors.append({"field": "self_evaluation", "error": "Self-evaluation not yet completed"})
        warnings.append({
            "field": "leadership_comment",
            "warning": "[MOCK AI] Comment appears too vague — consider adding specifics",
        })
        status = "fail" if errors else "pass"
        if status == "pass":
            await sheet_repository.update_status(db, sheet_id, "validated")
        return {"sheet_id": sheet_id, "status": status, "errors": errors, "warnings": warnings}

    async def batch_validate(self, db: AsyncSession, sheet_ids: list[str]) -> dict:
        results = []
        for sid in sheet_ids:
            sheet = await sheet_repository.get_by_id(db, sid)
            if sheet:
                results.append(await self.validate_sheet(db, sid))
            else:
                results.append({
                    "sheet_id": sid,
                    "status": "error",
                    "errors": [{"field": "sheet", "error": "Not found"}],
                    "warnings": [],
                })
        return {"results": results}

    async def migrate(
        self,
        db: AsyncSession,
        from_period: str,
        to_period: str,
        employee_updates: list[dict] | None = None,
    ) -> dict:
        migrated = []
        all_sheets = await sheet_repository.get_all(db)
        source_sheets = [s for s in all_sheets if s.period == from_period]
        updates_map = {u["employee_id"]: u for u in (employee_updates or [])}

        for src in source_sheets:
            new_grade = updates_map.get(src.employee_id, {}).get("new_grade", src.grade)
            new_scoring = scoring_service.get_scoring(src.position, new_grade)
            sheet_id = f"SHEET-{to_period}-{uuid.uuid4().hex[:6].upper()}"
            sheet = Sheet(
                sheet_id=sheet_id,
                employee_id=src.employee_id,
                employee_name=src.employee_name,
                email=src.email,
                position=src.position,
                grade=new_grade,
                period=to_period,
                status="created",
                scoring_criteria=new_scoring,
                google_sheet_url=f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}",
                migrated_from=src.sheet_id,
            )
            await sheet_repository.save(db, sheet)
            migrated.append({
                "sheet_id": sheet_id,
                "employee_id": src.employee_id,
                "old_grade": src.grade,
                "new_grade": new_grade,
            })
        return {"status": "success", "migrated": len(migrated), "sheets": migrated}


sheet_service = SheetService()
