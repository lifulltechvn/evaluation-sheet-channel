"""Google Drive / Sheets service — copy template spreadsheets."""

import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "/app/credentials.json")


def _get_drive_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


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


def copy_template_to_folder(template_file_id: str, folder_id: str, file_name: str) -> dict:
    """
    Copy a Google Sheet template into a target folder with a given name.
    Returns {"spreadsheet_id": ..., "spreadsheet_url": ...}
    """
    service = _get_drive_service()
    body = {"name": file_name, "parents": [folder_id]}
    copied = service.files().copy(
        fileId=template_file_id,
        body=body,
        supportsAllDrives=True,
    ).execute()
    spreadsheet_id = copied["id"]
    return {
        "spreadsheet_id": spreadsheet_id,
        "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
    }
