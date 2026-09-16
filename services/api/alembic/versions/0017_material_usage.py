"""material usage tracking (Phase 6d)

Revision ID: 0017
Revises: 0016
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "material_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("maintenance_tickets.id"), nullable=False
        ),
        sa.Column("item", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("unit_cost", sa.Float, nullable=False),
        sa.Column("is_wastage", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("logged_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expense_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("expenses.id"), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_material_usage_ticket_id", "material_usage", ["ticket_id"])


def downgrade() -> None:
    op.drop_index("ix_material_usage_ticket_id", table_name="material_usage")
    op.drop_table("material_usage")
