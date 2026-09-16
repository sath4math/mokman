"""service category catalog (Phase 5d)

Revision ID: 0013
Revises: 0012
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # Reuses the existing ticket_priority enum type (created in 0006) --
    # no CREATE TYPE here.
    ticket_priority = postgresql.ENUM(name="ticket_priority", create_type=False)

    op.create_table(
        "service_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("default_priority", ticket_priority, nullable=False, server_default="medium"),
        sa.Column("estimated_completion_hours", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )


def downgrade() -> None:
    op.drop_table("service_categories")
