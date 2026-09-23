import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.modules.assets.service import get_asset
from app.modules.documents.schemas import DocumentConfirm
from app.modules.inspections.service import get_inspection
from app.modules.inspections.service import require_party as require_inspection_party
from app.modules.insurance.service import get_policy
from app.modules.leases.service import get_lease
from app.modules.leases.service import require_party as require_lease_party
from app.modules.owner.service import OwnerProfileAccessError
from app.modules.properties.service import get_owned_property, get_property_by_id
from app.modules.renovation.service import get_project


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
        # Admin manages properties on behalf of an owner (onboarding,
        # uploading photos/videos) -- same admin-bypass shape as every
        # /properties/{id} read endpoint already uses.
        if role == "admin":
            get_property_by_id(db, owner_id)
        else:
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
    elif owner_type == "asset":
        asset = get_asset(db, owner_id)
        get_owned_property(db, user_id, asset.property_id)
    elif owner_type == "insurance_policy":
        policy = get_policy(db, owner_id)
        get_owned_property(db, user_id, policy.property_id)
    elif owner_type == "renovation_project":
        project = get_project(db, owner_id)
        get_owned_property(db, user_id, project.property_id)
    elif owner_type == "owner_profile":
        # owner_id here is the profile's user_id (OwnerProfile's own PK) --
        # no row lookup needed, just confirm the caller is that owner or an
        # admin (who needs to view KYC documents to approve/reject them).
        if role != "admin" and user_id != owner_id:
            raise OwnerProfileAccessError
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
