"""add current_rank and template_id to users

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    pass  # columns moved to 0001_init_schema_and_seed_data


def downgrade():
    pass
