"""Data access layer for evaluation sheets (in-memory mock store)."""

# Mock Data Store — will be replaced by real DB later
SHEETS_DB: dict[str, dict] = {}


def get_all(
    period: str | None = None,
    status: str | None = None,
    position: str | None = None,
) -> list[dict]:
    results = list(SHEETS_DB.values())
    if period:
        results = [s for s in results if s["period"] == period]
    if status:
        results = [s for s in results if s["status"] == status]
    if position:
        results = [s for s in results if s["position"] == position]
    return results


def get_by_id(sheet_id: str) -> dict | None:
    return SHEETS_DB.get(sheet_id)


def save(sheet: dict) -> None:
    SHEETS_DB[sheet["sheet_id"]] = sheet


def update_status(sheet_id: str, status: str) -> bool:
    if sheet_id not in SHEETS_DB:
        return False
    SHEETS_DB[sheet_id]["status"] = status
    return True


def get_by_period(period: str) -> list[dict]:
    return [s for s in SHEETS_DB.values() if s["period"] == period]
