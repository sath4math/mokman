"""maintenance tickets

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    ticket_priority = sa.Enum("low", "medium", "high", "urgent", name="ticket_priority")
    ticket_status = sa.Enum("open", "assigned", "in_progress", "resolved", "closed", name="ticket_status")

    op.create_table(
        "maintenance_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("priority", ticket_priority, nullable=False, server_default="medium"),
        sa.Column("status", ticket_status, nullable=False, server_default="open"),
        sa.Column("raised_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_maintenance_tickets_property_id", "maintenance_tickets", ["property_id"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_tickets_property_id", table_name="maintenance_tickets")
    op.drop_table("maintenance_tickets")

    sa.Enum(name="ticket_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="ticket_priority").drop(op.get_bind(), checkfirst=True)
