"""owner package/plan tier foundation (Phase 6a)

Revision ID: 0014
Revises: 0013
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # No create_table to piggyback the enum-type creation on this time
    # (unlike every enum introduced in 0006/0008) -- this is a column
    # added to an existing table, so the type has to be created explicitly
    # first.
    owner_package = sa.Enum("starter", "managed", "full_care", "complete", name="owner_package")
    owner_package.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "owner_profiles",
        sa.Column("package", owner_package, nullable=False, server_default="starter"),
    )


def downgrade() -> None:
    op.drop_column("owner_profiles", "package")
    sa.Enum(name="owner_package").drop(op.get_bind(), checkfirst=True)
