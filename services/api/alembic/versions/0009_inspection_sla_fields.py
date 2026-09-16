"""inspection formalization and ticket SLA fields

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE inspection_type ADD VALUE IF NOT EXISTS 'scheduled'")
    op.execute("ALTER TYPE inspection_type ADD VALUE IF NOT EXISTS 'ticket_triggered'")

    op.add_column("inspections", sa.Column("scheduled_for", sa.Date, nullable=True))
    op.add_column(
        "inspections",
        sa.Column(
            "triggered_by_ticket_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("maintenance_tickets.id"),
            nullable=True,
        ),
    )
    op.add_column("inspections", sa.Column("follow_up_notes", sa.Text, nullable=True))
    op.add_column("inspections", sa.Column("follow_up_due_on", sa.Date, nullable=True))

    op.add_column("maintenance_tickets", sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("maintenance_tickets", sa.Column("sla_breached_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("maintenance_tickets", "sla_breached_at")
    op.drop_column("maintenance_tickets", "sla_due_at")

    op.drop_column("inspections", "follow_up_due_on")
    op.drop_column("inspections", "follow_up_notes")
    op.drop_column("inspections", "triggered_by_ticket_id")
    op.drop_column("inspections", "scheduled_for")

    # Postgres can't drop enum values; downgrading leaves 'scheduled' and
    # 'ticket_triggered' in the type, which is harmless (no rows can
    # reference them once the app code rejects those values again).
