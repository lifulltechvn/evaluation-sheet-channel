"""add h1/h2 score columns to evaluations

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-05
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade():
    # Phase hiện tại (1 hoặc 2)
    op.add_column("evaluations", sa.Column("phase", sa.SmallInteger(), server_default="1", nullable=False))

    # Điểm & xếp hạng lần 1
    op.add_column("evaluations", sa.Column("h1_score", sa.Float(), nullable=True))
    op.add_column("evaluations", sa.Column("h1_rank", sa.String(10), nullable=True))
    op.add_column("evaluations", sa.Column("h1_approved_by", sa.String(36), nullable=True))
    op.add_column("evaluations", sa.Column("h1_approved_at", sa.DateTime(), nullable=True))

    # Điểm & xếp hạng lần 2
    op.add_column("evaluations", sa.Column("h2_score", sa.Float(), nullable=True))
    op.add_column("evaluations", sa.Column("h2_rank", sa.String(10), nullable=True))
    op.add_column("evaluations", sa.Column("h2_approved_by", sa.String(36), nullable=True))
    op.add_column("evaluations", sa.Column("h2_approved_at", sa.DateTime(), nullable=True))

    # FK constraints cho approved_by
    op.create_foreign_key("fk_eval_h1_approved_by", "evaluations", "users", ["h1_approved_by"], ["id"])
    op.create_foreign_key("fk_eval_h2_approved_by", "evaluations", "users", ["h2_approved_by"], ["id"])

    # Check constraint: phase chỉ được là 1 hoặc 2
    op.create_check_constraint("ck_eval_phase", "evaluations", "phase IN (1, 2)")


def downgrade():
    op.drop_constraint("ck_eval_phase", "evaluations", type_="check")
    op.drop_constraint("fk_eval_h2_approved_by", "evaluations", type_="foreignkey")
    op.drop_constraint("fk_eval_h1_approved_by", "evaluations", type_="foreignkey")

    op.drop_column("evaluations", "h2_approved_at")
    op.drop_column("evaluations", "h2_approved_by")
    op.drop_column("evaluations", "h2_rank")
    op.drop_column("evaluations", "h2_score")
    op.drop_column("evaluations", "h1_approved_at")
    op.drop_column("evaluations", "h1_approved_by")
    op.drop_column("evaluations", "h1_rank")
    op.drop_column("evaluations", "h1_score")
    op.drop_column("evaluations", "phase")
