from datetime import datetime, timedelta, timezone

from app.services.image_storage_service import ImageStorageError, delete_draft_image_keys
from app.storage.db import get_db_session
from app.storage.schema import (
    AppSessionRecord,
    DraftImageRecord,
    ListingDraftRecord,
    OAuthStateRecord,
    SellerConnectionRecord,
)

_LAST_CLEANUP_RUN: datetime | None = None
_CLEANUP_INTERVAL = timedelta(minutes=15)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def maybe_run_periodic_cleanup() -> None:
    global _LAST_CLEANUP_RUN

    now = _utc_now()
    if _LAST_CLEANUP_RUN and now - _LAST_CLEANUP_RUN < _CLEANUP_INTERVAL:
        return

    _LAST_CLEANUP_RUN = now
    cleanup_expired_sessions()


def cleanup_expired_sessions() -> None:
    now = _utc_now()

    with get_db_session() as session:
        expired_sessions = [
            record
            for record in session.query(AppSessionRecord).all()
            if (_parse_datetime(record.expires_at) or now) <= now
        ]

        for session_record in expired_sessions:
            draft_images = (
                session.query(DraftImageRecord)
                .filter(DraftImageRecord.session_id == session_record.id)
                .all()
            )
            storage_keys = [row.storage_key for row in draft_images if row.storage_key]
            if storage_keys:
                try:
                    delete_draft_image_keys(storage_keys)
                except ImageStorageError:
                    pass

            for row in draft_images:
                session.delete(row)

            for draft in (
                session.query(ListingDraftRecord)
                .filter(ListingDraftRecord.session_id == session_record.id)
                .all()
            ):
                session.delete(draft)

            for state in (
                session.query(OAuthStateRecord)
                .filter(OAuthStateRecord.session_id == session_record.id)
                .all()
            ):
                session.delete(state)

            for connection in (
                session.query(SellerConnectionRecord)
                .filter(SellerConnectionRecord.session_id == session_record.id)
                .all()
            ):
                session.delete(connection)

            session.delete(session_record)

        if expired_sessions:
            session.commit()
