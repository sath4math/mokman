"""ticket quality control: checklists, check-in/out, rework (Phase 5b)

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "checklist_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category", sa.String(100), nullable=False, unique=True),
        sa.Column("items", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )

    op.add_column("maintenance_tickets", sa.Column("checklist", postgresql.JSONB, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_in_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_in_latitude", sa.Float, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_in_longitude", sa.Float, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_out_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_out_latitude", sa.Float, nullable=True))
    op.add_column("maintenance_tickets", sa.Column("check_out_longitude", sa.Float, nullable=True))
    op.add_column(
        "maintenance_tickets", sa.Column("rework_count", sa.Integer, nullable=False, server_default="0")
    )


def downgrade() -> None:
    op.drop_column("maintenance_tickets", "rework_count")
    op.drop_column("maintenance_tickets", "check_out_longitude")
    op.drop_column("maintenance_tickets", "check_out_latitude")
    op.drop_column("maintenance_tickets", "check_out_at")
    op.drop_column("maintenance_tickets", "check_in_longitude")
    op.drop_column("maintenance_tickets", "check_in_latitude")
    op.drop_column("maintenance_tickets", "check_in_at")
    op.drop_column("maintenance_tickets", "checklist")

    op.drop_table("checklist_templates")
