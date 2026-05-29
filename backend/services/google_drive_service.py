"""Google Drive / Sheets service — copy template spreadsheets."""

import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "/app/credentials.json")


def _get_drive_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def _retry(fn, max_retries=5):
    """Execute fn with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return fn()
        except HttpError as e:
            if e.resp.status in (403, 429) and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def list_files_in_folder(folder_id: str) -> dict:
    """Return a dict of {file_name: file_id} for all files in a folder."""
    service = _get_drive_service()
    files = {}
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageSize=1000,
            pageToken=page_token,
        ).execute()
        for f in resp.get("files", []):
            files[f["name"]] = f["id"]
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return files


def get_or_create_folder(parent_id: str, folder_name: str) -> str:
    """Get existing folder by name in parent, or create it. Returns folder ID."""
    service = _get_drive_service()
    q = f"'{parent_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    resp = _retry(lambda: service.files().list(q=q, fields="files(id)", supportsAllDrives=True, includeItemsFromAllDrives=True).execute())
    files = resp.get("files", [])
    if files:
        return files[0]["id"]
    body = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    folder = _retry(lambda: service.files().create(body=body, fields="id", supportsAllDrives=True).execute())
    return folder["id"]


def copy_template_to_folder(template_file_id: str, folder_id: str, file_name: str) -> dict:
    """
    Copy a Google Sheet template into a target folder with a given name.
    Returns {"spreadsheet_id": ..., "spreadsheet_url": ...}
    """
    service = _get_drive_service()
    body = {"name": file_name, "parents": [folder_id]}
    copied = _retry(lambda: service.files().copy(
        fileId=template_file_id,
        body=body,
        supportsAllDrives=True,
    ).execute())
    spreadsheet_id = copied["id"]
    return {
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
    }


def _get_sheets_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_evaluation_sheet(spreadsheet_id: str) -> dict:
    """
    Read evaluation data from a spreadsheet.
    Returns: {
        "employee_name": str,
        "job_title": str,
        "level": str,
        "period": str,
        "technical_skills": [{"skill": str, "goal": str, "self_comment": str, "self_score": int|None, "leader_comment": str, "leader_score": int|None}],
        "guidelines": [{"item": str, "self_comment": str, "self_score": str|None, "leader_comment": str, "leader_score": str|None}],
    }
    """
    service = _get_sheets_service()

    # Get tab names
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    tab_names = [s["properties"]["title"] for s in meta["sheets"]]

    # Find TS and GL tabs for the latest period
    ts_tab = next((t for t in tab_names if t.startswith("TS_")), None)
    gl_tab = next((t for t in tab_names if t.startswith("GL_")), None)

    # Read header info from TS tab (or GL if no TS)
    header_tab = ts_tab or gl_tab or tab_names[0]
    header = _retry(lambda: service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=f"'{header_tab}'!A1:C8"
    ).execute()).get("values", [])

    employee_name = _cell(header, 5, 1)  # Row 6, Col B
    job_title = _cell(header, 6, 1)      # Row 7, Col B
    level = _cell(header, 7, 1)          # Row 8, Col B
    period = _cell(header, 2, 2) or _cell(header, 3, 2)  # Row 3 or 4, Col C

    result = {
        "employee_name": employee_name,
        "job_title": job_title,
        "level": level,
        "period": period,
        "technical_skills": [],
        "guidelines": [],
        "historical_scores": {},
    }

    # Read G Level tab (historical scores)
    g_level_tab = "G Level" if "G Level" in tab_names else None
    if g_level_tab:
        gl_header = _retry(lambda: service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{g_level_tab}'!A16:F16"
        ).execute()).get("values", [])
        period_headers = gl_header[0][1:] if gl_header and len(gl_header[0]) > 1 else []

        gl_scores = _retry(lambda: service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{g_level_tab}'!A17:F28"
        ).execute()).get("values", [])
        for row in gl_scores:
            skill_name = _safe(row, 0) if row else ""
            if not skill_name:
                continue
            scores_by_period = {}
            for idx, period_name in enumerate(period_headers):
                score = _parse_score(_safe(row, idx + 1))
                if score is not None:
                    scores_by_period[period_name] = score
            if scores_by_period:
                result["historical_scores"][skill_name] = scores_by_period

    # Read Technical Skills tab
    if ts_tab:
        ts_data = _retry(lambda: service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{ts_tab}'!A23:L50"
        ).execute()).get("values", [])
        for row in ts_data:
            if len(row) < 2 or not row[0].strip():
                continue
            skill_name = _safe(row, 1)
            if not skill_name:
                continue
            result["technical_skills"].append({
                "skill": skill_name,
                "goal": _safe(row, 3),
                "self_comment": _safe(row, 5),
                "self_score": _parse_score(_safe(row, 7)),
                "leader_comment": _safe(row, 8),
                "leader_score": _parse_score(_safe(row, 10)),
            })

    # Read Guidelines tab
    if gl_tab:
        gl_data = _retry(lambda: service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=f"'{gl_tab}'!A14:K25"
        ).execute()).get("values", [])
        for row in gl_data:
            if len(row) < 2 or not row[0].strip():
                continue
            item_name = _safe(row, 1)
            if not item_name:
                continue
            result["guidelines"].append({
                "item": item_name,
                "self_comment": _safe(row, 3),
                "self_score": _safe(row, 5),
                "leader_comment": _safe(row, 6),
                "leader_score": _safe(row, 8),
            })

    return result


def _cell(rows, row_idx, col_idx):
    """Safely get a cell value."""
    if row_idx < len(rows) and col_idx < len(rows[row_idx]):
        return rows[row_idx][col_idx].strip()
    return ""


def _safe(row, idx):
    """Safely get value from row by index."""
    return row[idx].strip() if idx < len(row) and row[idx].strip() else ""


def _parse_score(val):
    """Parse a score value to int, return None if not a number."""
    if not val:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None
