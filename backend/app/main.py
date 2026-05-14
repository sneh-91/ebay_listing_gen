from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from app.config import get_settings
from app.routes.ebay import router as ebay_router
from app.routes.health import router as health_router
from app.routes.listings import router as listings_router
from app.services.cleanup_service import maybe_run_periodic_cleanup
from app.services.session_service import (
    apply_session_cookie,
    resolve_or_create_session,
)
from app.storage.db import init_database

settings = get_settings()

app = FastAPI(title="ListCraft AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(listings_router)
app.include_router(ebay_router)


@app.middleware("http")
async def attach_session(request: Request, call_next):
    maybe_run_periodic_cleanup()
    session_cookie = request.cookies.get(settings.session_cookie_name)
    resolved_session = resolve_or_create_session(session_cookie)
    request.state.session_id = resolved_session.session_id
    request.state.session_expires_at = resolved_session.expires_at

    response = await call_next(request)
    apply_session_cookie(response, resolved_session)
    return response


@app.on_event("startup")
def startup() -> None:
    init_database()
