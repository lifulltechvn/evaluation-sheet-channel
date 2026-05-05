from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.database import Base


class Sheet(Base):
    __tablename__ = "sheets"

    sheet_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    employee_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    scoring_criteria: Mapped[dict] = mapped_column(JSON, nullable=True)
    google_sheet_url: Mapped[str] = mapped_column(String(500), nullable=True)
    migrated_from: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
