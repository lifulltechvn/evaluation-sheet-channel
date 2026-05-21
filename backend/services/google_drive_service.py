"""Google Drive / Sheets service — copy template spreadsheets."""

import os
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive"]
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
