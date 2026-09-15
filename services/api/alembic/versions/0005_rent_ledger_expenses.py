"""rent invoices, ledger, expenses

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-16

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    invoice_status = sa.Enum(
        "pending", "partially_paid", "paid", "overdue", "cancelled", name="invoice_status"
    )
    expense_status = sa.Enum("pending", "approved", "rejected", name="expense_status")
    ledger_entry_type = sa.Enum(
        "rent_payment",
        "mokman_fee",
        "deposit_collected",
        "deposit_deduction",
        "deposit_refund",
        "expense",
        name="ledger_entry_type",
    )

    op.add_column("inspections", sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "rent_invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lease_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leases.id"), nullable=False),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column("amount_due", sa.Float, nullable=False),
        sa.Column("status", invoice_status, nullable=False, server_default="pending"),
        *_timestamp_columns(),
    )
    op.create_index("ix_rent_invoices_lease_id", "rent_invoices", ["lease_id"])
    op.create_index("ix_rent_invoices_property_id", "rent_invoices", ["property_id"])

    op.create_table(
        "expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", expense_status, nullable=False, server_default="pending"),
        sa.Column("submitted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("ix_expenses_property_id", "expenses", ["property_id"])

    op.create_table(
        "ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("lease_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leases.id"), nullable=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rent_invoices.id"), nullable=True),
        sa.Column("expense_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("expenses.id"), nullable=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id"), nullable=True),
        sa.Column("entry_type", ledger_entry_type, nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("method", sa.String(30), nullable=True),
        sa.Column("reference_note", sa.Text, nullable=True),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ledger_entries_property_id", "ledger_entries", ["property_id"])
    op.create_index("ix_ledger_entries_lease_id", "ledger_entries", ["lease_id"])
    op.create_index("ix_ledger_entries_invoice_id", "ledger_entries", ["invoice_id"])
    op.create_index("ix_ledger_entries_expense_id", "ledger_entries", ["expense_id"])
    op.create_index("ix_ledger_entries_inspection_id", "ledger_entries", ["inspection_id"])


def downgrade() -> None:
    op.drop_index("ix_ledger_entries_inspection_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_expense_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_invoice_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_lease_id", table_name="ledger_entries")
    op.drop_index("ix_ledger_entries_property_id", table_name="ledger_entries")
    op.drop_table("ledger_entries")

    op.drop_index("ix_expenses_property_id", table_name="expenses")
    op.drop_table("expenses")

    op.drop_index("ix_rent_invoices_property_id", table_name="rent_invoices")
    op.drop_index("ix_rent_invoices_lease_id", table_name="rent_invoices")
    op.drop_table("rent_invoices")

    op.drop_column("inspections", "settled_at")

    sa.Enum(name="ledger_entry_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="expense_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="invoice_status").drop(op.get_bind(), checkfirst=True)
