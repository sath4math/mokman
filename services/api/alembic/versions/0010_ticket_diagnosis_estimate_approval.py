"""ticket diagnosis, estimate, approval (Phase 5a)

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'diagnosed'")
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'estimated'")
    op.execute("ALTER TYPE ticket_status ADD VALUE IF NOT EXISTS 'approved'")

    op.add_column("maintenance_tickets", sa.Column("diagnosis_notes", sa.Text, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("diagnosed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column("diagnosed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("maintenance_tickets", sa.Column("estimated_cost", sa.Float, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("estimated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column("estimated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("maintenance_tickets", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "maintenance_tickets",
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("maintenance_tickets", "approved_by")
    op.drop_column("maintenance_tickets", "approved_at")
    op.drop_column("maintenance_tickets", "estimated_by")
    op.drop_column("maintenance_tickets", "estimated_at")
    op.drop_column("maintenance_tickets", "estimated_cost")
    op.drop_column("maintenance_tickets", "diagnosed_by")
    op.drop_column("maintenance_tickets", "diagnosed_at")
    op.drop_column("maintenance_tickets", "diagnosis_notes")

    # Postgres can't drop enum values; downgrading leaves 'diagnosed'/
    # 'estimated'/'approved' in the type, harmless once the app code
    # stops writing them (same note as 0009's inspection_type values).
