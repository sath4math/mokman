"""fair-use frequency/value limits (Phase 6c)

Revision ID: 0016
Revises: 0015
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("service_eligibility_rules", sa.Column("max_occurrences", sa.Integer, nullable=True))
    op.add_column("service_eligibility_rules", sa.Column("period_days", sa.Integer, nullable=True))
    op.add_column("service_eligibility_rules", sa.Column("max_value", sa.Float, nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column("fair_use_breached", sa.Boolean, nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("maintenance_tickets", "fair_use_breached")
    op.drop_column("service_eligibility_rules", "max_value")
    op.drop_column("service_eligibility_rules", "period_days")
    op.drop_column("service_eligibility_rules", "max_occurrences")
