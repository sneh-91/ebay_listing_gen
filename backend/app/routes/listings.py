from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from app.models.draft_update import DraftUpdatePayload
from app.models.listing import ListingDraft
from app.services.session_service import get_request_session_id
from app.services.openai_service import (
    ListingGenerationError,
    generate_listing_with_openai,
)
from app.services.image_storage_service import (
    delete_draft_images,
    ImageStorageError,
    StoredDraftImage,
    upload_draft_image,
)
from app.storage.draft_store import get_draft, save_draft
from app.utils.image_processing import (
    ImageProcessingError,
    preprocess_image_for_openai,
    preprocess_image_for_storage,
)

router = APIRouter(prefix="/api", tags=["listings"])

MAX_IMAGES = 3
MAX_FILE_SIZE_BYTES = 8 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def _raise_validation_error(message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
    raise HTTPException(status_code=status_code, detail=message)


def _validate_upload(upload: UploadFile) -> None:
    file_extension = Path(upload.filename or "").suffix.lower()

    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        _raise_validation_error(
            f'"{upload.filename or "uploaded file"}" is not a supported image format.'
        )

    if file_extension and file_extension not in ALLOWED_EXTENSIONS:
        _raise_validation_error(
            f'"{upload.filename or "uploaded file"}" uses an unsupported image extension.'
        )


@router.post("/generate-listing", response_model=ListingDraft)
async def generate_listing(
    request: Request,
    images: list[UploadFile] | None = File(default=None),
    condition: str | None = Form(default=None),
    known_issues: str | None = Form(default=None, alias="knownIssues"),
    included_accessories: str | None = Form(default=None, alias="includedAccessories"),
    desired_price: str | None = Form(default=None, alias="desiredPrice"),
    seller_notes: str | None = Form(default=None, alias="sellerNotes"),
) -> ListingDraft:
    if not images:
        _raise_validation_error("Upload at least one image to generate a listing draft.")

    if len(images) > MAX_IMAGES:
        _raise_validation_error(f"You can upload up to {MAX_IMAGES} images per listing draft.")

    processed_images: list[str] = []
    storage_images: list[tuple[bytes, str]] = []

    for upload in images:
        _validate_upload(upload)

        contents = await upload.read()
        await upload.seek(0)

        if not contents:
            _raise_validation_error(f'"{upload.filename or "uploaded file"}" is empty.')

        if len(contents) > MAX_FILE_SIZE_BYTES:
            _raise_validation_error(
                f'"{upload.filename or "uploaded file"}" exceeds the 8 MB file size limit.',
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            processed_images.append(
                preprocess_image_for_openai(
                    file_bytes=contents,
                    filename=upload.filename or "uploaded file",
                )
            )
            storage_images.append(
                preprocess_image_for_storage(
                    file_bytes=contents,
                    filename=upload.filename or "uploaded file",
                )
            )
        except ImageProcessingError as exc:
            _raise_validation_error(str(exc), status.HTTP_400_BAD_REQUEST)

    try:
        ai_draft = generate_listing_with_openai(
            image_data_urls=processed_images,
            condition=condition,
            known_issues=known_issues,
            included_accessories=included_accessories,
            desired_price=desired_price,
            seller_notes=seller_notes,
        )
    except ListingGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    draft = ListingDraft(
        draftId=f"draft-{uuid4().hex[:12]}",
        **ai_draft.model_dump(),
        imageUrls=[],
    )
    stored_images: list[StoredDraftImage] = []
    try:
        for index, (image_bytes, mime_type) in enumerate(storage_images):
            stored_images.append(
                upload_draft_image(
                    draft_id=draft.draftId,
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    sort_order=index,
                )
            )
    except ImageStorageError as exc:
        delete_draft_images(stored_images)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    draft.imageUrls = [image.public_url for image in stored_images]
    try:
        return save_draft(
            draft,
            get_request_session_id(request),
            image_assets=stored_images,
        )
    except ValueError as exc:
        delete_draft_images(stored_images)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception:
        delete_draft_images(stored_images)
        raise


@router.get("/drafts/{draft_id}", response_model=ListingDraft)
async def read_draft(draft_id: str, request: Request) -> ListingDraft:
    draft = get_draft(draft_id, get_request_session_id(request))
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    return draft


@router.put("/drafts/{draft_id}", response_model=ListingDraft)
async def update_draft(draft_id: str, payload: DraftUpdatePayload, request: Request) -> ListingDraft:
    session_id = get_request_session_id(request)
    existing_draft = get_draft(draft_id, session_id)
    if not existing_draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

    updated_draft = existing_draft.model_copy(
        update={
            "title": payload.title,
            "categorySuggestion": payload.categorySuggestion,
            "condition": payload.condition,
            "description": payload.description,
            "itemSpecifics": payload.itemSpecifics,
            "priceSuggestion": existing_draft.priceSuggestion.model_copy(
                update={
                    "amount": payload.priceSuggestion.amount,
                    "rationale": payload.priceSuggestion.rationale,
                }
            ),
        }
    )
    return save_draft(updated_draft, session_id)
