from sqlalchemy import (
    Column, String, Text, Float, Date, Boolean, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"
    id          = Column(String(36), primary_key=True)
    name        = Column(String(50), nullable=False, unique=True)
    permissions = Column(JSONB, nullable=False)
    created_at  = Column(DateTime, server_default=func.now())


class Team(Base):
    __tablename__ = "teams"
    id        = Column(String(36), primary_key=True)
    name      = Column(String(100), nullable=False)
    parent_id = Column(String(36), ForeignKey("teams.id"), nullable=True)
    type      = Column(String(10), nullable=False)
    __table_args__ = (CheckConstraint("type IN ('UNIT','GROUP')", name="ck_team_type"),)


class User(Base):
    __tablename__ = "users"
    id         = Column(String(36), primary_key=True)
    email      = Column(String(100), nullable=False, unique=True)
    full_name  = Column(String(100), nullable=False)
    role_id    = Column(String(36), ForeignKey("roles.id"), nullable=False)
    team_id    = Column(String(36), ForeignKey("teams.id"), nullable=True)
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status     = Column(String(10), server_default="active")
    deleted_at = Column(DateTime, nullable=True)
    __table_args__ = (CheckConstraint("status IN ('active','inactive')", name="ck_user_status"),)


class EvaluationPeriod(Base):
    __tablename__ = "evaluation_periods"
    id         = Column(String(36), primary_key=True)
    name       = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date   = Column(Date, nullable=False)
    folder_id  = Column(String(100), nullable=True)
    status     = Column(String(10), server_default="active")
    created_at = Column(DateTime, server_default=func.now())
    __table_args__ = (CheckConstraint("status IN ('active','closed')", name="ck_period_status"),)


class Template(Base):
    __tablename__ = "templates"
    id             = Column(String(36), primary_key=True)
    name           = Column(String(100), nullable=False)
    google_file_id = Column(String(100), nullable=False)
    description    = Column(Text, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())
    updated_at     = Column(DateTime, server_default=func.now())


class Evaluation(Base):
    __tablename__ = "evaluations"
    id                 = Column(String(36), primary_key=True)
    employee_id        = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    template_id        = Column(String(36), ForeignKey("templates.id"), nullable=False)
    period_id          = Column(String(36), ForeignKey("evaluation_periods.id"), nullable=False)
    spreadsheet_id     = Column(String(100), nullable=False)
    spreadsheet_url    = Column(Text, nullable=False)
    status             = Column(String(30), server_default="Self_Evaluating")
    current_handler_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    final_score        = Column(Float, nullable=True)
    rank               = Column(String(10), nullable=True)
    created_at         = Column(DateTime, server_default=func.now())
    updated_at         = Column(DateTime, server_default=func.now())
    deleted_at         = Column(DateTime, nullable=True)
    __table_args__ = (
        CheckConstraint(
            "status IN ('Self_Evaluating','Leader_Reviewing','Manager_Reviewing','Completed')",
            name="ck_eval_status"
        ),
    )


class EvaluationContentRefinement(Base):
    __tablename__ = "evaluation_content_refinements"
    id                = Column(String(36), primary_key=True)
    evaluation_id     = Column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False)
    check_type        = Column(String(20), nullable=True)
    original_content  = Column(Text, nullable=True)
    suggested_content = Column(Text, nullable=True)
    comment           = Column(String(255), nullable=True)
    is_applied        = Column(Boolean, server_default="false", nullable=False)
    created_at        = Column(DateTime, server_default=func.now())
    __table_args__ = (
        CheckConstraint("check_type IN ('SPELLING', 'TRANSLATION', 'FORMATTING')", name="ck_refinement_check_type"),
        Index("idx_refinements_evaluation_id", "evaluation_id"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id          = Column(String(36), primary_key=True, server_default="gen_random_uuid()::text")
    actor_id    = Column(String(36), ForeignKey("users.id"), nullable=False)
    action      = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id   = Column(String(36), nullable=True)
    details     = Column(JSONB, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())
    __table_args__ = (
        Index("idx_audit_actor_time", "actor_id", "created_at"),
        Index("idx_audit_action", "action"),
    )
