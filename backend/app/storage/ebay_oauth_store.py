from datetime import datetime, timezone

from app.models.ebay_oauth import EbayOAuthTokenSet
from app.storage.db import get_db_session
from app.storage.schema import OAuthStateRecord, SellerConnectionRecord

GLOBAL_CONNECTION_KEY = "__global__"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _prune_expired_states() -> None:
    now = _utc_now()
    with get_db_session() as session:
        records = session.query(OAuthStateRecord).all()
        removed = False
        for record in records:
            if _parse_datetime(record.expires_at) <= now:
                session.delete(record)
                removed = True
        if removed:
            session.commit()


def save_pending_state(state: str, expires_at: datetime) -> None:
    _prune_expired_states()
    now = _serialize_datetime(_utc_now())

    with get_db_session() as session:
        record = session.get(OAuthStateRecord, state)
        if record:
            record.expires_at = _serialize_datetime(expires_at)
            record.created_at = now
        else:
            session.add(
                OAuthStateRecord(
                    state=state,
                    session_id=None,
                    expires_at=_serialize_datetime(expires_at),
                    created_at=now,
                )
            )
        session.commit()


def consume_pending_state(state: str) -> bool:
    _prune_expired_states()
    with get_db_session() as session:
        record = session.get(OAuthStateRecord, state)
        if not record:
            return False

        expires_at = _parse_datetime(record.expires_at)
        session.delete(record)
        session.commit()
        return expires_at > _utc_now()


def save_token_set(token_set: EbayOAuthTokenSet) -> EbayOAuthTokenSet:
    now = _serialize_datetime(_utc_now())

    with get_db_session() as session:
        record = session.get(SellerConnectionRecord, GLOBAL_CONNECTION_KEY)
        if record:
            record.access_token = token_set.access_token
            record.refresh_token = token_set.refresh_token
            record.token_type = token_set.token_type
            record.scope = token_set.scope
            record.expires_at = _serialize_datetime(token_set.expires_at)
            record.environment = token_set.environment
            record.marketplace_id = token_set.marketplace_id
            record.updated_at = now
        else:
            session.add(
                SellerConnectionRecord(
                    connection_key=GLOBAL_CONNECTION_KEY,
                    session_id=None,
                    access_token=token_set.access_token,
                    refresh_token=token_set.refresh_token,
                    token_type=token_set.token_type,
                    scope=token_set.scope,
                    expires_at=_serialize_datetime(token_set.expires_at),
                    environment=token_set.environment,
                    marketplace_id=token_set.marketplace_id,
                    created_at=now,
                    updated_at=now,
                )
            )
        session.commit()

    return EbayOAuthTokenSet.model_validate(token_set.model_dump())


def get_token_set() -> EbayOAuthTokenSet | None:
    with get_db_session() as session:
        record = session.get(SellerConnectionRecord, GLOBAL_CONNECTION_KEY)
        if not record:
            return None

        return EbayOAuthTokenSet(
            access_token=record.access_token,
            refresh_token=record.refresh_token,
            token_type=record.token_type,
            scope=record.scope,
            expires_at=_parse_datetime(record.expires_at),
            environment=record.environment,
            marketplace_id=record.marketplace_id,
        )
