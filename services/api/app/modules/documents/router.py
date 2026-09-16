import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.storage import (
    build_object_key,
    delete_object,
    generate_presigned_download,
    generate_presigned_upload,
)
from app.database import get_db
from app.modules.assets.service import AssetNotFoundError
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.documents.schemas import (
    DocumentConfirm,
    DocumentOut,
    DownloadUrlOut,
    PresignRequest,
    PresignResponse,
)
from app.modules.documents.service import (
    DocumentNotFoundError,
    UnsupportedDocumentOwnerTypeError,
    create_document,
    delete_document,
    get_document,
    list_documents,
)
from app.modules.documents.service import verify_document_access as _verify_document_access
from app.modules.inspections.service import InspectionNotFoundError, NotPartyToInspectionError
from app.modules.insurance.service import InsurancePolicyNotFoundError
from app.modules.leases.service import LeaseNotFoundError, NotPartyToLeaseError
from app.modules.maintenance.service import NotPartyToTicketError, TicketNotFoundError
from app.modules.properties.service import PropertyNotFoundError

router = APIRouter(prefix="/documents", tags=["documents"])


def _verify_ownership(db: Session, current: CurrentUser, owner_type: str, owner_id: uuid.UUID) -> None:
    """Thin HTTP wrapper around documents.service.verify_document_access
    (moved there in Phase 7a so the AI Document Assistant can reuse it)."""
    try:
        _verify_document_access(db, current.user.id, current.role, owner_type, owner_id)
    except PropertyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found") from None
    except LeaseNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lease not found") from None
    except NotPartyToLeaseError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this lease") from None
    except InspectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this inspection") from None
    except TicketNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found") from None
    except NotPartyToTicketError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this ticket") from None
    except AssetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found") from None
    except InsurancePolicyNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found") from None
    except UnsupportedDocumentOwnerTypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported owner_type: {owner_type}"
        ) from None


@router.post("/presign", response_model=PresignResponse)
def presign(
    data: PresignRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PresignResponse:
    _verify_ownership(db, current, data.owner_type, data.owner_id)
    key = build_object_key(data.owner_type, data.owner_id, data.filename)
    upload_url = generate_presigned_upload(key, data.content_type)
    return PresignResponse(upload_url=upload_url, s3_key=key)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def confirm(
    data: DocumentConfirm,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentOut:
    _verify_ownership(db, current, data.owner_type, data.owner_id)
    return DocumentOut.model_validate(create_document(db, data))


@router.get("", response_model=list[DocumentOut])
def list_for_owner(
    owner_type: str,
    owner_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentOut]:
    _verify_ownership(db, current, owner_type, owner_id)
    return [DocumentOut.model_validate(d) for d in list_documents(db, owner_type, owner_id)]


@router.get("/{document_id}/download", response_model=DownloadUrlOut)
def download(
    document_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DownloadUrlOut:
    try:
        document = get_document(db, document_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from None
    _verify_ownership(db, current, document.owner_type, document.owner_id)
    return DownloadUrlOut(download_url=generate_presigned_download(document.s3_key))


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    document_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        document = get_document(db, document_id)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from None
    _verify_ownership(db, current, document.owner_type, document.owner_id)
    delete_object(document.s3_key)
    delete_document(db, document_id)
