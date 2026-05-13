from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.draft_update import DraftUpdatePayload
from app.models.listing import ListingDraft
from app.services.mock_listing_service import build_mock_listing_draft
from app.storage.draft_store import get_draft, save_draft

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
    images: list[UploadFile] = File(...),
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

    draft = build_mock_listing_draft(
        image_count=len(images),
        condition=condition,
        known_issues=known_issues,
        included_accessories=included_accessories,
        desired_price=desired_price,
        seller_notes=seller_notes,
    )
    return save_draft(draft)


@router.get("/drafts/{draft_id}", response_model=ListingDraft)
async def read_draft(draft_id: str) -> ListingDraft:
    draft = get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    return draft


@router.put("/drafts/{draft_id}", response_model=ListingDraft)
async def update_draft(draft_id: str, payload: DraftUpdatePayload) -> ListingDraft:
    existing_draft = get_draft(draft_id)
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
    return save_draft(updated_draft)
