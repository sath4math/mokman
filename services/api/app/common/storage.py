import uuid

import boto3

from app.config import settings

_PRESIGN_EXPIRY_SECONDS = 900

_client = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url or None,
    aws_access_key_id=settings.s3_access_key_id or None,
    aws_secret_access_key=settings.s3_secret_access_key or None,
    region_name=settings.s3_region or None,
)


def build_object_key(owner_type: str, owner_id: uuid.UUID, filename: str) -> str:
    safe_filename = filename.replace("/", "_")
    return f"{owner_type}/{owner_id}/{uuid.uuid4()}-{safe_filename}"


def generate_presigned_upload(key: str, content_type: str) -> str:
    return _client.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.s3_bucket, "Key": key, "ContentType": content_type},
        ExpiresIn=_PRESIGN_EXPIRY_SECONDS,
    )


def generate_presigned_download(key: str) -> str:
    return _client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=_PRESIGN_EXPIRY_SECONDS,
    )


def delete_object(key: str) -> None:
    _client.delete_object(Bucket=settings.s3_bucket, Key=key)


def get_object_bytes(key: str) -> tuple[bytes, str]:
    """Fetches an object's bytes and content-type directly (Phase 7a).

    Content-type comes back from S3/R2 as object metadata set at
    presigned-upload time (generate_presigned_upload's ContentType
    param) — no separate content-type column needed on Document.
    """
    response = _client.get_object(Bucket=settings.s3_bucket, Key=key)
    body = response["Body"].read()
    content_type = response.get("ContentType", "application/octet-stream")
    return body, content_type
