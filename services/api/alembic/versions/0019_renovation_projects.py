"""renovation & project management (Phase 8b)

Revision ID: 0019
Revises: 0018
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    project_status = sa.Enum(
        "requested", "approved", "in_progress", "completed", "cancelled", name="project_status"
    )
    project_status.create(op.get_bind(), checkfirst=True)
    project_status_ref = postgresql.ENUM(name="project_status", create_type=False)

    op.create_table(
        "renovation_projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("status", project_status_ref, nullable=False, server_default="requested"),
        sa.Column("budget_amount", sa.Float, nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("end_date", sa.Date, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("warranty_expires_on", sa.Date, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_renovation_projects_property_id", "renovation_projects", ["property_id"])

    op.create_table(
        "project_milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("renovation_projects.id"), nullable=False
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("payment_amount", sa.Float, nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expense_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("expenses.id"), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_project_milestones_project_id", "project_milestones", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_project_milestones_project_id", table_name="project_milestones")
    op.drop_table("project_milestones")
    op.drop_index("ix_renovation_projects_property_id", table_name="renovation_projects")
    op.drop_table("renovation_projects")
    sa.Enum(name="project_status").drop(op.get_bind(), checkfirst=True)
