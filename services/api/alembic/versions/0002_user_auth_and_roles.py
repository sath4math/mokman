"""user auth (hashed_password) and seed roles

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-15

"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLES = ["owner", "tenant", "field_staff", "admin"]

roles_table = sa.table(
    "roles",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("name", sa.String),
)


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hashed_password", sa.String(255), nullable=False, server_default=""),
    )
    op.alter_column("users", "hashed_password", server_default=None)

    # created_at/updated_at are left out here and filled by the roles table's
    # own server_default=now() (defined in 0001) — sa.func.now() can't be
    # rendered as a literal value for an offline/--sql bulk insert.
    op.bulk_insert(
        roles_table,
        [{"id": uuid.uuid4(), "name": name} for name in ROLES],
    )


def downgrade() -> None:
    op.execute(roles_table.delete().where(roles_table.c.name.in_(ROLES)))
    op.drop_column("users", "hashed_password")
