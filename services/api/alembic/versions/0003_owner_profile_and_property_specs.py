"""owner profile, authorized representatives, property specs

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # Each enum is used exactly once below, so its first use in create_table
    # emits CREATE TYPE on its own — no separate .create() call needed (and
    # calling it explicitly here would emit a duplicate CREATE TYPE).
    ownership_type = sa.Enum("single", "joint", name="ownership_type")
    kyc_status = sa.Enum("pending", "verified", "rejected", name="kyc_status")

    op.create_table(
        "owner_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("pan_number", sa.String(20), nullable=True),
        sa.Column("id_proof_type", sa.String(20), nullable=True),
        sa.Column("id_proof_number", sa.String(50), nullable=True),
        sa.Column("bank_account_number", sa.String(50), nullable=True),
        sa.Column("bank_ifsc", sa.String(20), nullable=True),
        sa.Column("bank_name", sa.String(255), nullable=True),
        sa.Column("ownership_type", ownership_type, nullable=False, server_default="single"),
        sa.Column("ownership_percentage", sa.Float, nullable=True),
        sa.Column("nominee_name", sa.String(255), nullable=True),
        sa.Column("nominee_relationship", sa.String(100), nullable=True),
        sa.Column("nominee_phone", sa.String(20), nullable=True),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(20), nullable=True),
        sa.Column("kyc_status", kyc_status, nullable=False, server_default="pending"),
        *_timestamp_columns(),
    )

    op.create_table(
        "authorized_representatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("relationship", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_authorized_representatives_owner_id", "authorized_representatives", ["owner_id"])

    op.add_column("properties", sa.Column("area_sqft", sa.Float, nullable=True))
    op.add_column("properties", sa.Column("num_floors", sa.Integer, nullable=True))
    op.add_column("properties", sa.Column("num_units", sa.Integer, nullable=True))
    op.add_column("properties", sa.Column("amenities", postgresql.ARRAY(sa.String), nullable=True))
    op.add_column("properties", sa.Column("furnishing_status", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("properties", "furnishing_status")
    op.drop_column("properties", "amenities")
    op.drop_column("properties", "num_units")
    op.drop_column("properties", "num_floors")
    op.drop_column("properties", "area_sqft")

    op.drop_index("ix_authorized_representatives_owner_id", table_name="authorized_representatives")
    op.drop_table("authorized_representatives")
    op.drop_table("owner_profiles")

    sa.Enum(name="kyc_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="ownership_type").drop(op.get_bind(), checkfirst=True)
