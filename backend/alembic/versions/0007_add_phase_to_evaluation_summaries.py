"""add phase to evaluation_summaries

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-05
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade():
    # Thêm cột phase (default = 1 cho data cũ)
    op.add_column("evaluation_summaries", sa.Column("phase", sa.SmallInteger(), server_default="1", nullable=False))

    # Xóa UNIQUE constraint cũ (evaluation_id)
    op.drop_constraint("evaluation_summaries_evaluation_id_key", "evaluation_summaries", type_="unique")

    # Tạo UNIQUE constraint mới (evaluation_id, phase) — 1 eval chỉ có tối đa 2 phase
    op.create_unique_constraint("uq_eval_summary_eval_phase", "evaluation_summaries", ["evaluation_id", "phase"])

    # Check constraint: phase chỉ được là 1 hoặc 2
    op.create_check_constraint("ck_summary_phase", "evaluation_summaries", "phase IN (1, 2)")


def downgrade():
    op.drop_constraint("ck_summary_phase", "evaluation_summaries", type_="check")
    op.drop_constraint("uq_eval_summary_eval_phase", "evaluation_summaries", type_="unique")

    # Khôi phục UNIQUE constraint cũ
    op.create_unique_constraint("evaluation_summaries_evaluation_id_key", "evaluation_summaries", ["evaluation_id"])

    op.drop_column("evaluation_summaries", "phase")
