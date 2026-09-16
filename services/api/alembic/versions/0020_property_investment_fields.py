"""investment intelligence: property cost basis (Phase 8c)

Revision ID: 0020
Revises: 0019
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("properties", sa.Column("purchase_price", sa.Float, nullable=True))
    op.add_column("properties", sa.Column("current_market_value", sa.Float, nullable=True))


def downgrade() -> None:
    op.drop_column("properties", "current_market_value")
    op.drop_column("properties", "purchase_price")
