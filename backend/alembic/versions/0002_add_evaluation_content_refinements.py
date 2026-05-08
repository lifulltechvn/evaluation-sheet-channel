"""add evaluation_content_refinements table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-05
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evaluation_content_refinements",
        sa.Column("id",                sa.String(36), primary_key=True),
        sa.Column("evaluation_id",     sa.String(36), sa.ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_type",        sa.String(20), nullable=True),
        sa.Column("original_content",  sa.Text, nullable=True),
        sa.Column("suggested_content", sa.Text, nullable=True),
        sa.Column("comment",           sa.String(255), nullable=True),
        sa.Column("is_applied",        sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at",        sa.DateTime, server_default=sa.func.now()),
        sa.CheckConstraint(
            "check_type IN ('SPELLING', 'TRANSLATION', 'FORMATTING')",
            name="ck_refinement_check_type"
        ),
    )

    # Index để tăng tốc truy vấn theo evaluation_id
    op.create_index(
        "idx_refinements_evaluation_id",
        "evaluation_content_refinements",
        ["evaluation_id"]
    )


def downgrade():
    op.drop_index("idx_refinements_evaluation_id", table_name="evaluation_content_refinements")
    op.drop_table("evaluation_content_refinements")
