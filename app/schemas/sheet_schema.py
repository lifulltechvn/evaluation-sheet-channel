from pydantic import BaseModel


class EmployeeInput(BaseModel):
    employee_id: str
    name: str
    email: str
    position: str
    grade: str


class GenerateRequest(BaseModel):
    period: str
    employees: list[EmployeeInput]


class MigrateRequest(BaseModel):
    from_period: str
    to_period: str
    employee_updates: list[dict] | None = None


class BatchSendRequest(BaseModel):
    sheet_ids: list[str]
