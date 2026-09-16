"""sale, transfer & exit (Phase 8d)

Revision ID: 0021
Revises: 0020
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    sale_status = sa.Enum(
        "listed", "under_negotiation", "agreement_signed", "completed", "cancelled", name="sale_status"
    )
    sale_status.create(op.get_bind(), checkfirst=True)
    sale_status_ref = postgresql.ENUM(name="sale_status", create_type=False)

    op.create_table(
        "property_sales",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("status", sale_status_ref, nullable=False, server_default="listed"),
        sa.Column("listing_price", sa.Float, nullable=True),
        sa.Column("sale_price", sa.Float, nullable=True),
        sa.Column("buyer_name", sa.String(255), nullable=True),
        sa.Column("buyer_contact", sa.String(255), nullable=True),
        sa.Column("agreement_date", sa.Date, nullable=True),
        sa.Column("settlement_date", sa.Date, nullable=True),
        sa.Column("ownership_transferred", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("utilities_transferred", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("society_transferred", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_property_sales_property_id", "property_sales", ["property_id"])


def downgrade() -> None:
    op.drop_index("ix_property_sales_property_id", table_name="property_sales")
    op.drop_table("property_sales")
    sa.Enum(name="sale_status").drop(op.get_bind(), checkfirst=True)
