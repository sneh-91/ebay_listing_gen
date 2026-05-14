from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.models.ebay_oauth import EbayConnectionStatus, EbayOAuthStartResponse
from app.services.ebay_oauth_service import (
    EbayOAuthError,
    build_authorization_url,
    exchange_authorization_code,
    get_configuration_status,
)

router = APIRouter(prefix="/api/ebay", tags=["ebay"])


def _frontend_redirect(status_value: str, message: str | None = None) -> RedirectResponse:
    settings = get_settings()
    query = {"ebay": status_value}
    if message:
        query["message"] = message

    redirect_url = f"{settings.frontend_url}/?{urlencode(query)}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/oauth/start", response_model=EbayOAuthStartResponse)
async def start_ebay_oauth() -> EbayOAuthStartResponse:
    try:
        return EbayOAuthStartResponse(authorizationUrl=build_authorization_url())
    except EbayOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/oauth/callback")
async def ebay_oauth_callback(
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
        exchange_authorization_code(code=code, state=state)
    except EbayOAuthError as exc:
        return _frontend_redirect("error", str(exc))

    return _frontend_redirect("connected")


@router.get("/status", response_model=EbayConnectionStatus)
async def ebay_status() -> EbayConnectionStatus:
    try:
        return get_configuration_status()
    except EbayOAuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
