"""cross-phase foundation: property hierarchy, RBAC, audit log, documents

Revision ID: 0001
Revises:
Create Date: 2026-09-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

property_status_enum = postgresql.ENUM(
    "vacant", "occupied", "under_maintenance", "inactive", name="property_status"
)


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    # First use (on `properties`) creates the PostgreSQL enum type; the second
    # use (on `units`) must pass create_type=False to avoid a duplicate
    # CREATE TYPE statement.
    status_col_first_use = sa.Enum(
        "vacant", "occupied", "under_maintenance", "inactive",
        name="property_status",
    )
    status_col_reuse = sa.Enum(
        "vacant", "occupied", "under_maintenance", "inactive",
        name="property_status", create_type=False,
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default=sa.false()),
        *_timestamp_columns(),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
    )

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        *_timestamp_columns(),
    )

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        *_timestamp_columns(),
    )

    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address_line", sa.String(500), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("postal_code", sa.String(20), nullable=False),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("status", status_col_first_use, nullable=False, server_default="vacant"),
        *_timestamp_columns(),
    )
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])

    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_buildings_property_id", "buildings", ["property_id"])

    op.create_table(
        "blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_blocks_building_id", "blocks", ["building_id"])

    op.create_table(
        "floors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blocks.id"), nullable=False),
        sa.Column("level", sa.Integer, nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_floors_block_id", "floors", ["block_id"])

    op.create_table(
        "units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("floor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("floors.id"), nullable=False),
        sa.Column("unit_number", sa.String(50), nullable=False),
        sa.Column("area_sqft", sa.Float, nullable=True),
        sa.Column("status", status_col_reuse, nullable=False, server_default="vacant"),
        *_timestamp_columns(),
    )
    op.create_index("ix_units_floor_id", "units", ["floor_id"])

    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_rooms_unit_id", "rooms", ["unit_id"])

    op.create_table(
        "parking_spots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("identifier", sa.String(50), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_parking_spots_property_id", "parking_spots", ["property_id"])

    op.create_table(
        "storage_units",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("identifier", sa.String(50), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_storage_units_property_id", "storage_units", ["property_id"])

    op.create_table(
        "common_areas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("ix_common_areas_property_id", "common_areas", ["property_id"])

    op.create_table(
        "role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_role_assignments_user_id", "role_assignments", ["user_id"])
    op.create_index("ix_role_assignments_property_id", "role_assignments", ["property_id"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_type", sa.String(50), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("s3_key", sa.String(1000), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("ocr_status", sa.String(20), nullable=False, server_default="pending"),
        *_timestamp_columns(),
    )
    op.create_index("ix_documents_owner_type", "documents", ["owner_type"])
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("before", postgresql.JSONB, nullable=True),
        sa.Column("after", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("documents")
    op.drop_table("role_assignments")
    op.drop_table("common_areas")
    op.drop_table("storage_units")
    op.drop_table("parking_spots")
    op.drop_table("rooms")
    op.drop_table("units")
    op.drop_table("floors")
    op.drop_table("blocks")
    op.drop_table("buildings")
    op.drop_table("properties")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
    property_status_enum.drop(op.get_bind(), checkfirst=True)
