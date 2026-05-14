from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def _build_engine():
    settings = get_settings()
    connect_args = {"check_same_thread": False} if _is_sqlite_url(settings.database_url) else {}
    return create_engine(settings.database_url, connect_args=connect_args)


engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def get_db_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_database() -> None:
    from app.storage import schema  # noqa: F401

    Base.metadata.create_all(bind=engine)
