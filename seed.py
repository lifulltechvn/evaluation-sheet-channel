"""Seed database with initial mock data."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import async_session
from app.models.employee import Employee
from app.models.history import EvaluationHistory


EMPLOYEES = [
    Employee(employee_id="EMP001", name="Nguyen Van A", email="a@example.com", position="application_engineer", grade="G2"),
    Employee(employee_id="EMP002", name="Tran Thi B", email="b@example.com", position="bse", grade="G1"),
    Employee(employee_id="EMP003", name="Le Van C", email="c@example.com", position="qa", grade="G3"),
    Employee(employee_id="EMP004", name="Pham Thi D", email="d@example.com", position="hr", grade="G0"),
    Employee(employee_id="EMP005", name="Hoang Van E", email="e@example.com", position="admin", grade="G1"),
]

HISTORY = [
    EvaluationHistory(employee_id="EMP001", period="2025-H2", grade="G2", position="application_engineer", total_score=82, google_sheet_url="https://docs.google.com/spreadsheets/d/mock-2025h2-001"),
    EvaluationHistory(employee_id="EMP001", period="2025-H1", grade="G1", position="application_engineer", total_score=75, google_sheet_url="https://docs.google.com/spreadsheets/d/mock-2025h1-001"),
    EvaluationHistory(employee_id="EMP002", period="2025-H2", grade="G1", position="bse", total_score=78, google_sheet_url="https://docs.google.com/spreadsheets/d/mock-2025h2-002"),
]


async def seed():
    async with async_session() as session:  # type: AsyncSession
        # Check if data already exists
        existing = await session.get(Employee, "EMP001")
        if existing:
            print("Data already seeded. Skipping.")
            return

        session.add_all(EMPLOYEES)
        session.add_all(HISTORY)
        await session.commit()
        print(f"Seeded {len(EMPLOYEES)} employees and {len(HISTORY)} history records.")


if __name__ == "__main__":
    asyncio.run(seed())
