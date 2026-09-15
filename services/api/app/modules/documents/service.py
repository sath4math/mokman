import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.modules.documents.schemas import DocumentConfirm


class DocumentNotFoundError(Exception):
    pass


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
