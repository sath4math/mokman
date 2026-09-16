import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.common.llm import AssistantNotConfiguredError
from app.database import get_db
from app.modules.assets.service import AssetNotFoundError
from app.modules.assistant.schemas import AssistantAskIn, AssistantAskOut
from app.modules.assistant.service import (
    NoInspectionPhotosError,
    UnsupportedDocumentTypeError,
    analyze_inspection_photos,
    ask_about_document,
    ask_owner_assistant,
)
from app.modules.auth.dependencies import CurrentUser, get_current_user
from app.modules.documents.service import DocumentNotFoundError, UnsupportedDocumentOwnerTypeError
from app.modules.inspections.service import InspectionNotFoundError, NotPartyToInspectionError
from app.modules.insurance.service import InsurancePolicyNotFoundError
from app.modules.leases.service import LeaseNotFoundError, NotPartyToLeaseError
from app.modules.maintenance.service import NotPartyToTicketError, TicketNotFoundError
from app.modules.properties.service import PropertyNotFoundError
from app.modules.renovation.service import ProjectNotFoundError

router = APIRouter(prefix="/assistant", tags=["assistant"])


def _not_configured() -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI assistant is not configured")


@router.post("/ask", response_model=AssistantAskOut)
def ask(
    data: AssistantAskIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistantAskOut:
    if current.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required")
    try:
        answer = ask_owner_assistant(db, current.user.id, data.question)
    except AssistantNotConfiguredError:
        raise _not_configured() from None
    return AssistantAskOut(answer=answer)


@router.post("/documents/{document_id}/ask", response_model=AssistantAskOut)
def ask_document(
    document_id: uuid.UUID,
    data: AssistantAskIn,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistantAskOut:
    try:
        answer = ask_about_document(db, current.user.id, current.role, document_id, data.question)
    except DocumentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found") from None
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
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except UnsupportedDocumentOwnerTypeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported document owner type") from None
    except UnsupportedDocumentTypeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="This document type isn't supported for Q&A (only images and PDFs are)",
        ) from None
    except AssistantNotConfiguredError:
        raise _not_configured() from None
    return AssistantAskOut(answer=answer)


@router.post("/inspections/{inspection_id}/analyze", response_model=AssistantAskOut)
def analyze_inspection(
    inspection_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssistantAskOut:
    try:
        answer = analyze_inspection_photos(db, current.user.id, inspection_id)
    except InspectionNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found") from None
    except NotPartyToInspectionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this inspection") from None
    except NoInspectionPhotosError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No analyzable photos attached to this inspection"
        ) from None
    except AssistantNotConfiguredError:
        raise _not_configured() from None
    return AssistantAskOut(answer=answer)
