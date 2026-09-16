"""vendor operations

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("service_category", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("gst_number", sa.String(20), nullable=True),
        sa.Column("pan_number", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )

    op.add_column(
        "maintenance_tickets",
        sa.Column("assigned_vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
    )
    op.add_column(
        "expenses",
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("expenses", "vendor_id")
    op.drop_column("maintenance_tickets", "assigned_vendor_id")
    op.drop_table("vendors")
