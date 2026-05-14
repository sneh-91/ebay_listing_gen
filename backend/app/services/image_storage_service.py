from dataclasses import dataclass
from urllib.parse import quote

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings


class ImageStorageError(Exception):
    pass


@dataclass
class StoredDraftImage:
    storage_key: str
    public_url: str
    mime_type: str
    sort_order: int


def _require_s3_configuration() -> None:
    settings = get_settings()
    if not settings.s3_bucket_name or not settings.s3_region:
        raise ImageStorageError(
            "S3 image storage is not configured on the backend."
        )


def _build_s3_client():
    settings = get_settings()
    return boto3.client("s3", region_name=settings.s3_region)


def _build_public_url(storage_key: str) -> str:
    settings = get_settings()
    if settings.s3_public_base_url:
        return f"{settings.s3_public_base_url.rstrip('/')}/{quote(storage_key)}"

    return (
        f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/"
        f"{quote(storage_key)}"
    )


def upload_draft_image(
    draft_id: str,
    image_bytes: bytes,
    mime_type: str,
    sort_order: int,
) -> StoredDraftImage:
    _require_s3_configuration()
    settings = get_settings()
    storage_key = f"{settings.s3_key_prefix.strip('/')}/{draft_id}/{sort_order + 1}.jpg"
    client = _build_s3_client()

    try:
        client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=storage_key,
            Body=image_bytes,
            ContentType=mime_type,
            CacheControl="public, max-age=31536000",
        )
    except (BotoCoreError, ClientError) as exc:
        raise ImageStorageError(
            "Unable to upload draft images to S3."
        ) from exc

    return StoredDraftImage(
        storage_key=storage_key,
        public_url=_build_public_url(storage_key),
        mime_type=mime_type,
        sort_order=sort_order,
    )


def delete_draft_images(images: list[StoredDraftImage]) -> None:
    if not images:
        return

    _require_s3_configuration()
    settings = get_settings()
    client = _build_s3_client()

    for image in images:
        try:
            client.delete_object(
                Bucket=settings.s3_bucket_name,
                Key=image.storage_key,
            )
        except (BotoCoreError, ClientError):
            continue


def delete_draft_image_keys(storage_keys: list[str]) -> None:
    if not storage_keys:
        return

    _require_s3_configuration()
    settings = get_settings()
    client = _build_s3_client()

    for storage_key in storage_keys:
        try:
            client.delete_object(
                Bucket=settings.s3_bucket_name,
                Key=storage_key,
            )
        except (BotoCoreError, ClientError):
            continue
