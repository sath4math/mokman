"""vendor polish and property ops (preventive maintenance, utilities, compliance)

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "vendor_rate_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("service_category", sa.String(100), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("rate", sa.Float, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_vendor_rate_cards_vendor_id", "vendor_rate_cards", ["vendor_id"])

    op.create_table(
        "vendor_ratings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column(
            "ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("maintenance_tickets.id"), nullable=False
        ),
        sa.Column("rated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_vendor_ratings_vendor_id", "vendor_ratings", ["vendor_id"])
    op.create_index("ix_vendor_ratings_ticket_id", "vendor_ratings", ["ticket_id"])

    op.create_table(
        "maintenance_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("frequency_days", sa.Integer, nullable=False),
        sa.Column("last_serviced_on", sa.Date, nullable=True),
        sa.Column("next_due_on", sa.Date, nullable=False),
        sa.Column("warranty_expires_on", sa.Date, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )
    op.create_index("ix_maintenance_schedules_property_id", "maintenance_schedules", ["property_id"])

    utility_responsibility = sa.Enum("owner", "tenant", name="utility_responsibility")

    op.create_table(
        "utility_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("utility_type", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(255), nullable=True),
        sa.Column("account_number", sa.String(100), nullable=True),
        sa.Column("responsibility", utility_responsibility, nullable=False, server_default="owner"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )
    op.create_index("ix_utility_connections_property_id", "utility_connections", ["property_id"])

    op.create_table(
        "utility_bills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "connection_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("utility_connections.id"),
            nullable=False,
        ),
        sa.Column("billing_period_start", sa.Date, nullable=False),
        sa.Column("billing_period_end", sa.Date, nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("meter_reading", sa.Float, nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_utility_bills_connection_id", "utility_bills", ["connection_id"])

    compliance_category = sa.Enum("society_maintenance", "property_tax", "other", name="compliance_category")

    op.create_table(
        "compliance_dues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("category", compliance_category, nullable=False, server_default="other"),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_reference", sa.String(255), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_compliance_dues_property_id", "compliance_dues", ["property_id"])


def downgrade() -> None:
    op.drop_index("ix_compliance_dues_property_id", table_name="compliance_dues")
    op.drop_table("compliance_dues")
    sa.Enum(name="compliance_category").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_utility_bills_connection_id", table_name="utility_bills")
    op.drop_table("utility_bills")

    op.drop_index("ix_utility_connections_property_id", table_name="utility_connections")
    op.drop_table("utility_connections")
    sa.Enum(name="utility_responsibility").drop(op.get_bind(), checkfirst=True)

    op.drop_index("ix_maintenance_schedules_property_id", table_name="maintenance_schedules")
    op.drop_table("maintenance_schedules")

    op.drop_index("ix_vendor_ratings_ticket_id", table_name="vendor_ratings")
    op.drop_index("ix_vendor_ratings_vendor_id", table_name="vendor_ratings")
    op.drop_table("vendor_ratings")

    op.drop_index("ix_vendor_rate_cards_vendor_id", table_name="vendor_rate_cards")
    op.drop_table("vendor_rate_cards")
