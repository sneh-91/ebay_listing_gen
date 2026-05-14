import json
from datetime import datetime, timezone

from app.models.listing import ListingDraft
from app.storage.db import get_db_session
from app.storage.schema import DraftImageRecord, ListingDraftRecord
from app.services.image_storage_service import StoredDraftImage


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _replace_draft_images(
    session,
    draft_id: str,
    session_id: str,
    image_assets: list[StoredDraftImage],
) -> None:
    existing_rows = (
        session.query(DraftImageRecord)
        .filter(DraftImageRecord.draft_id == draft_id)
        .all()
    )
    for row in existing_rows:
        session.delete(row)

    for image in image_assets:
        session.add(
            DraftImageRecord(
                draft_id=draft_id,
                session_id=session_id,
                storage_key=image.storage_key,
                public_url=image.public_url,
                mime_type=image.mime_type,
                sort_order=image.sort_order,
                created_at=_utc_now_iso(),
            )
        )


def _load_draft_image_urls(session, draft_id: str, session_id: str) -> list[str]:
    rows = (
        session.query(DraftImageRecord)
        .filter(
            DraftImageRecord.draft_id == draft_id,
            DraftImageRecord.session_id == session_id,
        )
        .order_by(DraftImageRecord.sort_order.asc(), DraftImageRecord.id.asc())
        .all()
    )
    return [row.public_url for row in rows if row.public_url]


def save_draft(
    draft: ListingDraft,
    session_id: str,
    image_assets: list[StoredDraftImage] | None = None,
) -> ListingDraft:
    now = _utc_now_iso()
    payload_json = draft.model_dump_json()

    with get_db_session() as session:
        record = session.get(ListingDraftRecord, draft.draftId)
        if record:
            if record.session_id != session_id:
                raise ValueError("Draft does not belong to the active session.")
            record.payload_json = payload_json
            record.updated_at = now
        else:
            session.add(
                ListingDraftRecord(
                    draft_id=draft.draftId,
                    session_id=session_id,
                    payload_json=payload_json,
                    created_at=now,
                    updated_at=now,
                )
            )

        if image_assets is not None:
            _replace_draft_images(
                session=session,
                draft_id=draft.draftId,
                session_id=session_id,
                image_assets=image_assets,
            )
        session.commit()
        image_urls = _load_draft_image_urls(session, draft.draftId, session_id)

    return ListingDraft.model_validate(
        {
            **json.loads(payload_json),
            "imageUrls": image_urls or draft.imageUrls,
        }
    )


def get_draft(draft_id: str, session_id: str) -> ListingDraft | None:
    with get_db_session() as session:
        record = session.get(ListingDraftRecord, draft_id)
        if not record or record.session_id != session_id:
            return None
        payload = json.loads(record.payload_json)
        payload["imageUrls"] = _load_draft_image_urls(session, draft_id, session_id)
        return ListingDraft.model_validate(payload)
