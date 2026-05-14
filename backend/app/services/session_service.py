from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import Request
from starlette.responses import Response

from app.config import get_settings
from app.storage.db import get_db_session
from app.storage.schema import AppSessionRecord


@dataclass
class ResolvedSession:
    session_id: str
    expires_at: datetime
    is_new: bool


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _build_expiration(now: datetime) -> datetime:
    settings = get_settings()
    return now + timedelta(days=settings.session_ttl_days)


def _create_session_id() -> str:
    return token_urlsafe(24)


def resolve_or_create_session(cookie_value: str | None) -> ResolvedSession:
    now = _utc_now()
    expires_at = _build_expiration(now)

    if cookie_value:
        with get_db_session() as session:
            record = session.get(AppSessionRecord, cookie_value)
            if record:
                stored_expiry = _parse_datetime(record.expires_at) if record.expires_at else now
                if stored_expiry > now:
                    record.updated_at = _serialize_datetime(now)
                    record.expires_at = _serialize_datetime(expires_at)
                    session.commit()
                    return ResolvedSession(
                        session_id=record.id,
                        expires_at=expires_at,
                        is_new=False,
                    )

    session_id = _create_session_id()
    with get_db_session() as session:
        session.add(
            AppSessionRecord(
                id=session_id,
                created_at=_serialize_datetime(now),
                updated_at=_serialize_datetime(now),
                expires_at=_serialize_datetime(expires_at),
            )
        )
        session.commit()

    return ResolvedSession(session_id=session_id, expires_at=expires_at, is_new=True)


def apply_session_cookie(response: Response, resolved_session: ResolvedSession) -> None:
    settings = get_settings()
    max_age = settings.session_ttl_days * 24 * 60 * 60
    response.set_cookie(
        key=settings.session_cookie_name,
        value=resolved_session.session_id,
        max_age=max_age,
        expires=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
        path="/",
    )


def get_request_session_id(request: Request) -> str:
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        raise RuntimeError("Session middleware did not resolve a session.")
    return session_id
