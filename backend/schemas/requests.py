from pydantic import BaseModel


class EmployeeInput(BaseModel):
    employee_id: str
    name: str
    email: str
    position: str  # application_engineer, bse, hr, admin, qa
    grade: str  # G0-G6


class GenerateRequest(BaseModel):
    period: str
    employees: list[EmployeeInput]


class MigrateRequest(BaseModel):
    from_period: str
    to_period: str
    employee_updates: list[dict] | None = None


class SendResultsRequest(BaseModel):
    period: str
    employee_ids: list[str]


class BatchSendRequest(BaseModel):
    sheet_ids: list[str]
