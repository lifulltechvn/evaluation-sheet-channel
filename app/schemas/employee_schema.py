from pydantic import BaseModel


class Employee(BaseModel):
    employee_id: str
    name: str
    email: str
    position: str
    grade: str
