"""ticket warranty, repeat-failure, cost-variance link (Phase 5c)

Revision ID: 0012
Revises: 0011
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("maintenance_tickets", sa.Column("warranty_expires_on", sa.Date, nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column("is_repeat_failure", sa.Boolean, nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "maintenance_tickets",
        sa.Column(
            "related_ticket_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("maintenance_tickets.id"),
            nullable=True,
        ),
    )

    op.add_column(
        "expenses",
        sa.Column(
            "ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("maintenance_tickets.id"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_column("expenses", "ticket_id")

    op.drop_column("maintenance_tickets", "related_ticket_id")
    op.drop_column("maintenance_tickets", "is_repeat_failure")
    op.drop_column("maintenance_tickets", "warranty_expires_on")
