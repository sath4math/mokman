"""tenant profile, lease, inspection

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    tenant_verification_status = sa.Enum("pending", "verified", "rejected", name="tenant_verification_status")
    lease_status = sa.Enum(
        "draft", "pending_acknowledgment", "active", "terminated", "expired", name="lease_status"
    )
    inspection_type = sa.Enum("move_in", "move_out", name="inspection_type")

    op.create_table(
        "tenant_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("id_proof_type", sa.String(20), nullable=True),
        sa.Column("id_proof_number", sa.String(50), nullable=True),
        sa.Column("occupants_count", sa.Integer, nullable=True),
        sa.Column("vehicles", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("pets", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(20), nullable=True),
        sa.Column("verification_status", tenant_verification_status, nullable=False, server_default="pending"),
        *_timestamp_columns(),
    )

    op.create_table(
        "leases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("monthly_rent", sa.Float, nullable=False),
        sa.Column("security_deposit", sa.Float, nullable=False),
        sa.Column("lock_in_period_months", sa.Integer, nullable=True),
        sa.Column("notice_period_days", sa.Integer, nullable=True),
        sa.Column("annual_escalation_percentage", sa.Float, nullable=True),
        sa.Column("responsibilities", sa.Text, nullable=True),
        sa.Column("status", lease_status, nullable=False, server_default="pending_acknowledgment"),
        sa.Column("owner_acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("previous_lease_id", postgresql.UUID(as_uuid=True), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_leases_property_id", "leases", ["property_id"])
    op.create_index("ix_leases_tenant_id", "leases", ["tenant_id"])
    op.create_foreign_key(
        "fk_leases_previous_lease_id", "leases", "leases", ["previous_lease_id"], ["id"]
    )

    op.create_table(
        "inspections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("lease_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leases.id"), nullable=True),
        sa.Column("inspection_type", inspection_type, nullable=False),
        sa.Column("conducted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("checklist", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("meter_readings", postgresql.JSONB, nullable=True),
        sa.Column("owner_signed_off_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_signed_off_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deposit_deduction", sa.Float, nullable=True),
        sa.Column("deposit_refund", sa.Float, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_inspections_property_id", "inspections", ["property_id"])
    op.create_index("ix_inspections_lease_id", "inspections", ["lease_id"])


def downgrade() -> None:
    op.drop_index("ix_inspections_lease_id", table_name="inspections")
    op.drop_index("ix_inspections_property_id", table_name="inspections")
    op.drop_table("inspections")

    op.drop_constraint("fk_leases_previous_lease_id", "leases", type_="foreignkey")
    op.drop_index("ix_leases_tenant_id", table_name="leases")
    op.drop_index("ix_leases_property_id", table_name="leases")
    op.drop_table("leases")

    op.drop_table("tenant_profiles")

    sa.Enum(name="inspection_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="lease_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tenant_verification_status").drop(op.get_bind(), checkfirst=True)
