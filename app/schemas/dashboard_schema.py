from pydantic import BaseModel


class DashboardStatus(BaseModel):
    total_sheets: int
    by_status: dict[str, int]
