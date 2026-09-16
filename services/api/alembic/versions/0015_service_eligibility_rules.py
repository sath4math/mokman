"""labour-service eligibility engine (Phase 6b)

Revision ID: 0015
Revises: 0014
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # Created explicitly, then referenced via create_type=False below --
    # op.create_table's DDL re-triggers CREATE TYPE for any Enum column
    # object that hasn't been told the type already exists (unlike
    # op.add_column, which doesn't), so the same object can't be reused
    # for both the explicit create() and the column type the way 0014 does.
    sa.Enum(
        "included", "chargeable", "third_party", "out_of_scope", "escalate", name="eligibility_outcome"
    ).create(op.get_bind(), checkfirst=True)
    eligibility_outcome = postgresql.ENUM(name="eligibility_outcome", create_type=False)

    # Reuses the existing owner_package enum type (created in 0014) --
    # no CREATE TYPE here.
    owner_package = postgresql.ENUM(name="owner_package", create_type=False)

    op.create_table(
        "service_eligibility_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "service_category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_categories.id"),
            nullable=False,
        ),
        sa.Column("package", owner_package, nullable=False),
        sa.Column("outcome", eligibility_outcome, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        *_timestamp_columns(),
        sa.UniqueConstraint("service_category_id", "package", name="uq_eligibility_category_package"),
    )
    op.create_index(
        "ix_service_eligibility_rules_service_category_id",
        "service_eligibility_rules",
        ["service_category_id"],
    )

    op.add_column(
        "maintenance_tickets",
        sa.Column("eligibility_outcome", eligibility_outcome, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("maintenance_tickets", "eligibility_outcome")
    op.drop_index("ix_service_eligibility_rules_service_category_id", table_name="service_eligibility_rules")
    op.drop_table("service_eligibility_rules")
    sa.Enum(name="eligibility_outcome").drop(op.get_bind(), checkfirst=True)
