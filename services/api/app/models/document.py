import uuid
from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, uuid_pk


class Document(Base, TimestampMixin):
    """Polymorphic document attachable to a property, unit, tenant, or lease.

    (owner_type, owner_id) identifies the attached record instead of a
    foreign key per entity type, since the set of attachable entities grows
    every phase (tenant/lease in Phase 2, etc.). Stored as an S3 object key,
    never a DB blob; OCR runs as an async job against ocr_status.
    """

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = uuid_pk()
    owner_type: Mapped[str] = mapped_column(String(50), index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    document_type: Mapped[str] = mapped_column(String(100))
    s3_key: Mapped[str] = mapped_column(String(1000))
    version: Mapped[int] = mapped_column(Integer, default=1)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(20), default="pending")
