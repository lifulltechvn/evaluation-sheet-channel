"""add division manager roles

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-21
"""
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        INSERT INTO roles (id, name, permissions) VALUES
        ('R6', 'Division Manager',         '{"all": true, "view_all": true, "manage_all": true}'),
        ('R7', 'Deputy Division Manager',  '{"all": true, "view_all": true, "manage_all": true}')
    """)
    op.execute("UPDATE users SET role_id = 'R6' WHERE id = 'U141'")
    op.execute("UPDATE users SET role_id = 'R7' WHERE id = 'U106'")


def downgrade():
    op.execute("UPDATE users SET role_id = 'R1' WHERE id = 'U141'")
    op.execute("UPDATE users SET role_id = 'R1' WHERE id = 'U106'")
    op.execute("DELETE FROM roles WHERE id IN ('R6', 'R7')")
