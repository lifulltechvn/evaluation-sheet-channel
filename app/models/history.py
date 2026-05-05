from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.database import Base


class EvaluationHistory(Base):
    __tablename__ = "evaluation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=True)
    google_sheet_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
