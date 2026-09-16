import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.modules.documents.schemas import DocumentConfirm
from app.modules.inspections.service import get_inspection
from app.modules.inspections.service import require_party as require_inspection_party
from app.modules.leases.service import get_lease
from app.modules.leases.service import require_party as require_lease_party
from app.modules.properties.service import get_owned_property


class DocumentNotFoundError(Exception):
    pass


class UnsupportedDocumentOwnerTypeError(Exception):
    pass


def verify_document_access(db: Session, user_id: uuid.UUID, role: str, owner_type: str, owner_id: uuid.UUID) -> None:
    """Authorizes a caller against the entity a document is attached to.

    Grows as new owner_types gain their own document ownership: 'property'
    (Phase 1), 'lease' and 'inspection' (Phase 2), 'ticket' (Phase 4).
    Moved from documents/router.py's _verify_ownership in Phase 7a so the
    AI Document Assistant can reuse the exact same access check a
    download uses, rather than duplicating it. The ticket branch imports
    maintenance.service locally -- that module already imports this one
    (list_documents), so a top-level import here would cycle.
    """
    if owner_type == "property":
        get_owned_property(db, user_id, owner_id)
    elif owner_type == "lease":
        lease = get_lease(db, owner_id)
        require_lease_party(db, lease, user_id)
    elif owner_type == "inspection":
        inspection = get_inspection(db, owner_id)
        require_inspection_party(db, inspection, user_id)
    elif owner_type == "ticket":
        from app.modules.maintenance.service import get_ticket, require_ticket_access

        ticket = get_ticket(db, owner_id)
        require_ticket_access(db, ticket, user_id, role)
    else:
        raise UnsupportedDocumentOwnerTypeError


def create_document(db: Session, data: DocumentConfirm) -> Document:
    document = Document(**data.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, owner_type: str, owner_id: uuid.UUID) -> list[Document]:
    return list(
        db.execute(
            select(Document).where(Document.owner_type == owner_type, Document.owner_id == owner_id)
        ).scalars()
    )


def get_document(db: Session, document_id: uuid.UUID) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise DocumentNotFoundError
    return document


def delete_document(db: Session, document_id: uuid.UUID) -> Document:
    document = get_document(db, document_id)
    db.delete(document)
    db.commit()
    return document
