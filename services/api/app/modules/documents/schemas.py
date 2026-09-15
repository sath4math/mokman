import uuid
from datetime import date

from pydantic import BaseModel


class PresignRequest(BaseModel):
    owner_type: str
    owner_id: uuid.UUID
    filename: str
    content_type: str


class PresignResponse(BaseModel):
    upload_url: str
    s3_key: str


class DocumentConfirm(BaseModel):
    owner_type: str
    owner_id: uuid.UUID
    document_type: str
    s3_key: str
    expiry_date: date | None = None


class DocumentOut(BaseModel):
    id: uuid.UUID
    owner_type: str
    owner_id: uuid.UUID
    document_type: str
    version: int
    expiry_date: date | None
    ocr_status: str

    model_config = {"from_attributes": True}


class DownloadUrlOut(BaseModel):
    download_url: str
