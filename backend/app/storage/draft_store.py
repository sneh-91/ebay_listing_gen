import json
from datetime import datetime, timezone

from app.models.listing import ListingDraft
from app.storage.db import get_db_session
from app.storage.schema import ListingDraftRecord


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_draft(draft: ListingDraft, session_id: str) -> ListingDraft:
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
        session.commit()

    return ListingDraft.model_validate_json(payload_json)


def get_draft(draft_id: str, session_id: str) -> ListingDraft | None:
    with get_db_session() as session:
        record = session.get(ListingDraftRecord, draft_id)
        if not record or record.session_id != session_id:
            return None
        return ListingDraft.model_validate(json.loads(record.payload_json))
