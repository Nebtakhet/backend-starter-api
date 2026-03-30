"""add is_admin to users

Revision ID: 17f4fb1e7d2d
Revises: 8e57f450a02c
Create Date: 2026-03-30 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "17f4fb1e7d2d"
down_revision = "8e57f450a02c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
