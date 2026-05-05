from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
