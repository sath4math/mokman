"""asset & inventory management + insurance management (Phase 8a)

Revision ID: 0018
Revises: 0017
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("purchase_cost", sa.Float, nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("warranty_expires_on", sa.Date, nullable=True),
        sa.Column("useful_life_years", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("disposed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disposed_reason", sa.String(255), nullable=True),
        sa.Column("replaced_by_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_assets_property_id", "assets", ["property_id"])
    op.create_foreign_key(
        "fk_assets_replaced_by_asset_id", "assets", "assets", ["replaced_by_asset_id"], ["id"]
    )

    op.add_column(
        "maintenance_tickets",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
    )
    op.add_column(
        "maintenance_schedules",
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
    )

    claim_status = sa.Enum(
        "filed", "under_review", "approved", "rejected", "settled", name="claim_status"
    )
    claim_status.create(op.get_bind(), checkfirst=True)
    claim_status_ref = postgresql.ENUM(name="claim_status", create_type=False)

    op.create_table(
        "insurance_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("policy_number", sa.String(100), nullable=False),
        sa.Column("insurer_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("premium_amount", sa.Float, nullable=False),
        sa.Column("premium_due_date", sa.Date, nullable=True),
        sa.Column("coverage_amount", sa.Float, nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        *_timestamp_columns(),
    )
    op.create_index("ix_insurance_policies_property_id", "insurance_policies", ["property_id"])

    op.create_table(
        "insurance_claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("insurance_policies.id"), nullable=False
        ),
        sa.Column("incident_date", sa.Date, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("claim_amount", sa.Float, nullable=False),
        sa.Column("status", claim_status_ref, nullable=False, server_default="filed"),
        sa.Column("surveyor_name", sa.String(255), nullable=True),
        sa.Column("settlement_amount", sa.Float, nullable=True),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_insurance_claims_policy_id", "insurance_claims", ["policy_id"])


def downgrade() -> None:
    op.drop_index("ix_insurance_claims_policy_id", table_name="insurance_claims")
    op.drop_table("insurance_claims")
    op.drop_index("ix_insurance_policies_property_id", table_name="insurance_policies")
    op.drop_table("insurance_policies")
    sa.Enum(name="claim_status").drop(op.get_bind(), checkfirst=True)

    op.drop_column("maintenance_schedules", "asset_id")
    op.drop_column("maintenance_tickets", "asset_id")

    op.drop_constraint("fk_assets_replaced_by_asset_id", "assets", type_="foreignkey")
    op.drop_index("ix_assets_property_id", table_name="assets")
    op.drop_table("assets")
