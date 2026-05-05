from pydantic import BaseModel


class SendResultsRequest(BaseModel):
    period: str
    employee_ids: list[str]
