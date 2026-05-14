from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.models.ebay_oauth import EbayConnectionStatus, EbayOAuthStartResponse
from app.models.ebay_category import EbayCategoryStatus
from app.models.ebay_setup import EbaySetupStatus
from app.services.ebay_oauth_service import (
    EbayOAuthError,
    build_authorization_url,
    exchange_authorization_code,
    get_configuration_status,
)
from app.services.ebay_setup_service import get_setup_status
from app.services.ebay_taxonomy_service import EbayTaxonomyError, get_category_status
from app.services.session_service import get_request_session_id
from app.storage.draft_store import get_draft

router = APIRouter(prefix="/api/ebay", tags=["ebay"])


def _frontend_redirect(status_value: str, message: str | None = None) -> RedirectResponse:
    settings = get_settings()
    query = {"ebay": status_value}
    if message:
        query["message"] = message

    redirect_url = f"{settings.frontend_url}/?{urlencode(query)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/oauth/start", response_model=EbayOAuthStartResponse)
async def start_ebay_oauth(request: Request) -> EbayOAuthStartResponse:
    try:
        return EbayOAuthStartResponse(
            authorizationUrl=build_authorization_url(get_request_session_id(request))
        )
    except EbayOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/oauth/callback")
async def ebay_oauth_callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
) -> RedirectResponse:
    if error:
        message = error_description or "eBay did not complete the OAuth consent flow."
        return _frontend_redirect("error", message)

    if not code or not state:
        return _frontend_redirect(
            "error",
            "The eBay OAuth callback is missing the required code or state value.",
        )

    try:
        exchange_authorization_code(
            code=code,
            state=state,
            session_id=get_request_session_id(request),
        )
    except EbayOAuthError as exc:
        return _frontend_redirect("error", str(exc))

    return _frontend_redirect("connected")


@router.get("/status", response_model=EbayConnectionStatus)
async def ebay_status(request: Request) -> EbayConnectionStatus:
    try:
        return get_configuration_status(get_request_session_id(request))
    except EbayOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/setup/status", response_model=EbaySetupStatus)
async def ebay_setup_status(
    request: Request,
    draftId: str = Query(...),
) -> EbaySetupStatus:
    session_id = get_request_session_id(request)
    draft = get_draft(draftId, session_id)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

    try:
        return get_setup_status(session_id, draft)
    except EbayOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/category/status", response_model=EbayCategoryStatus)
async def ebay_category_status(
    request: Request,
    draftId: str = Query(...),
) -> EbayCategoryStatus:
    session_id = get_request_session_id(request)
    draft = get_draft(draftId, session_id)
    if not draft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")

    try:
        return get_category_status(session_id, draft)
    except EbayTaxonomyError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
