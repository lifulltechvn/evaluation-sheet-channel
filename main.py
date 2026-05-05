from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="Evaluation Sheet API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Models ---

class Employee(BaseModel):
    employee_id: str
    name: str
    email: str
    position: str  # application_engineer, bse, hr, admin, qa
    grade: str  # G0-G6

class GenerateRequest(BaseModel):
    period: str
    employees: list[Employee]

class MigrateRequest(BaseModel):
    from_period: str
    to_period: str
    employee_updates: list[dict] | None = None

class SendResultsRequest(BaseModel):
    period: str
    employee_ids: list[str]

class BatchSendRequest(BaseModel):
    sheet_ids: list[str]

# --- Mock Data Store ---

EMPLOYEES_DB: dict[str, dict] = {
    "EMP001": {"employee_id": "EMP001", "name": "Nguyen Van A", "email": "a@example.com", "position": "application_engineer", "grade": "G2"},
    "EMP002": {"employee_id": "EMP002", "name": "Tran Thi B", "email": "b@example.com", "position": "bse", "grade": "G1"},
    "EMP003": {"employee_id": "EMP003", "name": "Le Van C", "email": "c@example.com", "position": "qa", "grade": "G3"},
    "EMP004": {"employee_id": "EMP004", "name": "Pham Thi D", "email": "d@example.com", "position": "hr", "grade": "G0"},
    "EMP005": {"employee_id": "EMP005", "name": "Hoang Van E", "email": "e@example.com", "position": "admin", "grade": "G1"},
}

SHEETS_DB: dict[str, dict] = {}
HISTORY_DB: dict[str, list] = {
    "EMP001": [
        {"period": "2025-H2", "grade": "G2", "position": "application_engineer", "total_score": 82, "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h2-001"},
        {"period": "2025-H1", "grade": "G1", "position": "application_engineer", "total_score": 75, "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h1-001"},
    ],
    "EMP002": [
        {"period": "2025-H2", "grade": "G1", "position": "bse", "total_score": 78, "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h2-002"},
    ],
}

# Scoring rules per position/grade (mock)
SCORING_RULES = {
    "application_engineer": {"G0": {"programming": 5, "communication": 3, "teamwork": 2}, "G1": {"programming": 1, "communication": 4, "teamwork": 3, "leadership": 2}, "G2": {"programming": 1, "communication": 3, "teamwork": 3, "leadership": 3}},
    "bse": {"G0": {"programming": 4, "communication": 4, "japanese": 2}, "G1": {"programming": 2, "communication": 4, "japanese": 2, "leadership": 2}},
    "qa": {"G0": {"testing": 5, "communication": 3, "documentation": 2}, "G1": {"testing": 3, "communication": 3, "documentation": 2, "leadership": 2}},
    "hr": {"G0": {"hr_knowledge": 5, "communication": 3, "organization": 2}},
    "admin": {"G0": {"admin_skills": 5, "communication": 3, "organization": 2}},
}

def _get_scoring(position: str, grade: str) -> dict:
    pos_rules = SCORING_RULES.get(position, {})
    return pos_rules.get(grade, pos_rules.get("G0", {}))

# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "Evaluation Sheet API", "docs": "/docs", "health": "/v1/health"}

@app.get("/v1/health")
def health():
    return {"status": "ok"}

# -- Sheets --

@app.post("/v1/sheets/generate")
def generate_sheets(req: GenerateRequest):
    created = []
    for emp in req.employees:
        sheet_id = f"SHEET-{req.period}-{uuid.uuid4().hex[:6].upper()}"
        scoring = _get_scoring(emp.position, emp.grade)
        sheet = {
            "sheet_id": sheet_id,
            "employee_id": emp.employee_id,
            "employee_name": emp.name,
            "email": emp.email,
            "position": emp.position,
            "grade": emp.grade,
            "period": req.period,
            "status": "created",
            "scoring_criteria": scoring,
            "google_sheet_url": f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}",
            "created_at": datetime.now().isoformat(),
        }
        SHEETS_DB[sheet_id] = sheet
        created.append({"sheet_id": sheet_id, "employee_id": emp.employee_id, "google_sheet_url": sheet["google_sheet_url"], "status": "created"})
    return {"status": "success", "sheets_created": len(created), "sheets": created}

@app.get("/v1/sheets")
def list_sheets(period: str | None = None, status: str | None = None, position: str | None = None):
    results = list(SHEETS_DB.values())
    if period:
        results = [s for s in results if s["period"] == period]
    if status:
        results = [s for s in results if s["status"] == status]
    if position:
        results = [s for s in results if s["position"] == position]
    return {"sheets": results, "total": len(results)}

@app.get("/v1/sheets/{sheet_id}")
def get_sheet(sheet_id: str):
    if sheet_id not in SHEETS_DB:
        raise HTTPException(404, "Sheet not found")
    return SHEETS_DB[sheet_id]

@app.post("/v1/sheets/{sheet_id}/send")
def send_sheet(sheet_id: str):
    if sheet_id not in SHEETS_DB:
        raise HTTPException(404, "Sheet not found")
    SHEETS_DB[sheet_id]["status"] = "sent"
    return {"status": "success", "message": f"[MOCK] Email sent to {SHEETS_DB[sheet_id]['email']}"}

@app.post("/v1/sheets/batch-send")
def batch_send(req: BatchSendRequest):
    results = []
    for sid in req.sheet_ids:
        if sid in SHEETS_DB:
            SHEETS_DB[sid]["status"] = "sent"
            results.append({"sheet_id": sid, "sent": True})
        else:
            results.append({"sheet_id": sid, "sent": False, "error": "Not found"})
    return {"status": "success", "results": results}

# -- Validation --

@app.post("/v1/sheets/{sheet_id}/validate")
def validate_sheet(sheet_id: str):
    if sheet_id not in SHEETS_DB:
        raise HTTPException(404, "Sheet not found")
    sheet = SHEETS_DB[sheet_id]
    # Mock validation - simulate AI validation results
    errors, warnings = [], []
    if sheet["status"] == "created":
        errors.append({"field": "self_evaluation", "error": "Self-evaluation not yet completed"})
    warnings.append({"field": "leadership_comment", "warning": "[MOCK AI] Comment appears too vague — consider adding specifics"})
    status = "fail" if errors else "pass"
    SHEETS_DB[sheet_id]["status"] = "validated" if status == "pass" else sheet["status"]
    return {"sheet_id": sheet_id, "status": status, "errors": errors, "warnings": warnings}

@app.post("/v1/sheets/batch-validate")
def batch_validate(req: BatchSendRequest):
    results = []
    for sid in req.sheet_ids:
        if sid in SHEETS_DB:
            results.append(validate_sheet(sid))
        else:
            results.append({"sheet_id": sid, "status": "error", "errors": [{"field": "sheet", "error": "Not found"}], "warnings": []})
    return {"results": results}

# -- Migration --

@app.post("/v1/sheets/migrate")
def migrate_sheets(req: MigrateRequest):
    migrated = []
    source_sheets = [s for s in SHEETS_DB.values() if s["period"] == req.from_period]
    updates_map = {u["employee_id"]: u for u in (req.employee_updates or [])}
    for src in source_sheets:
        new_grade = updates_map.get(src["employee_id"], {}).get("new_grade", src["grade"])
        new_scoring = _get_scoring(src["position"], new_grade)
        sheet_id = f"SHEET-{req.to_period}-{uuid.uuid4().hex[:6].upper()}"
        sheet = {**src, "sheet_id": sheet_id, "period": req.to_period, "grade": new_grade, "status": "created", "scoring_criteria": new_scoring, "google_sheet_url": f"https://docs.google.com/spreadsheets/d/mock-{sheet_id}", "created_at": datetime.now().isoformat(), "migrated_from": src["sheet_id"]}
        SHEETS_DB[sheet_id] = sheet
        migrated.append({"sheet_id": sheet_id, "employee_id": src["employee_id"], "old_grade": src["grade"], "new_grade": new_grade})
    return {"status": "success", "migrated": len(migrated), "sheets": migrated}

# -- Notifications --

@app.post("/v1/notifications/send-results")
def send_results(req: SendResultsRequest):
    sent = []
    for eid in req.employee_ids:
        emp = EMPLOYEES_DB.get(eid)
        if emp:
            sent.append({"employee_id": eid, "email": emp["email"], "sent": True, "message": f"[MOCK] Result email sent to {emp['email']}"})
        else:
            sent.append({"employee_id": eid, "sent": False, "error": "Employee not found"})
    return {"status": "success", "results": sent}

# -- History --

@app.get("/v1/employees/{employee_id}/history")
def get_history(employee_id: str):
    if employee_id not in EMPLOYEES_DB:
        raise HTTPException(404, "Employee not found")
    return {"employee_id": employee_id, "history": HISTORY_DB.get(employee_id, [])}

# -- Dashboard --

@app.get("/v1/dashboard/status")
def dashboard_status():
    counts: dict[str, int] = {}
    for s in SHEETS_DB.values():
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    return {"total_sheets": len(SHEETS_DB), "by_status": counts}

@app.get("/v1/employees")
def list_employees():
    result = []
    for emp in EMPLOYEES_DB.values():
        sheets = [s for s in SHEETS_DB.values() if s["employee_id"] == emp["employee_id"]]
        latest = max(sheets, key=lambda x: x["created_at"]) if sheets else None
        result.append({**emp, "latest_sheet_status": latest["status"] if latest else "none", "latest_period": latest["period"] if latest else None})
    return {"employees": result, "total": len(result)}
