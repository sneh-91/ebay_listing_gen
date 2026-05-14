from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.db import Base


class AppSessionRecord(Base):
    __tablename__ = "app_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)
    expires_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class OAuthStateRecord(Base):
    __tablename__ = "oauth_states"

    state: Mapped[str] = mapped_column(String(128), primary_key=True)
    session_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("app_sessions.id"),
        nullable=True,
        index=True,
    )
    expires_at: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)


class SellerConnectionRecord(Base):
    __tablename__ = "seller_connections"

    connection_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("app_sessions.id"),
        nullable=True,
        index=True,
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_type: Mapped[str] = mapped_column(String(64), nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[str] = mapped_column(String(40), nullable=False)
    environment: Mapped[str] = mapped_column(String(32), nullable=False)
    marketplace_id: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)


class ListingDraftRecord(Base):
    __tablename__ = "listing_drafts"

    draft_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("app_sessions.id"),
        nullable=True,
        index=True,
    )
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)


class DraftImageRecord(Base):
    __tablename__ = "draft_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    draft_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("listing_drafts.draft_id"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("app_sessions.id"),
        nullable=True,
        index=True,
    )
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    public_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
