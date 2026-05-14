import base64
import json
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models.ebay_oauth import EbayConnectionStatus, EbayOAuthTokenSet
from app.storage.ebay_oauth_store import (
    consume_pending_state,
    get_token_set,
    save_pending_state,
    save_token_set,
)

EBAY_SCOPE_SELL_INVENTORY = "https://api.ebay.com/oauth/api_scope/sell.inventory"
DEFAULT_SCOPES = [EBAY_SCOPE_SELL_INVENTORY]
STATE_TTL_MINUTES = 10
ACCESS_TOKEN_REFRESH_BUFFER_SECONDS = 60


class EbayOAuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _is_configured() -> bool:
    settings = get_settings()
    return bool(
        settings.ebay_client_id
        and settings.ebay_client_secret
        and settings.ebay_redirect_uri
    )


def _require_configuration() -> None:
    if not _is_configured():
        raise EbayOAuthError(
            "eBay OAuth is not configured on the backend.",
            status_code=500,
        )


def _get_authorization_endpoint() -> str:
    settings = get_settings()
    if settings.ebay_env == "production":
        return "https://auth.ebay.com/oauth2/authorize"
    return "https://auth.sandbox.ebay.com/oauth2/authorize"


def _get_token_endpoint() -> str:
    settings = get_settings()
    if settings.ebay_env == "production":
        return "https://api.ebay.com/identity/v1/oauth2/token"
    return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"


def _basic_auth_header() -> str:
    settings = get_settings()
    credentials = f"{settings.ebay_client_id}:{settings.ebay_client_secret}".encode(
        "utf-8"
    )
    encoded = base64.b64encode(credentials).decode("ascii")
    return f"Basic {encoded}"


def _exchange_token_request(payload: dict[str, str]) -> dict:
    body = urlencode(payload).encode("utf-8")
    request = Request(
        _get_token_endpoint(),
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": _basic_auth_header(),
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(response_text)
            description = payload.get("error_description") or payload.get("error")
        except json.JSONDecodeError:
            description = None

        raise EbayOAuthError(
            description or "eBay OAuth token exchange failed.",
            status_code=502,
        ) from exc
    except URLError as exc:
        raise EbayOAuthError(
            "Unable to reach eBay OAuth services from the backend.",
            status_code=502,
        ) from exc


def _build_token_set(token_payload: dict, refresh_token: str | None = None) -> EbayOAuthTokenSet:
    settings = get_settings()
    resolved_refresh_token = token_payload.get("refresh_token") or refresh_token
    if not resolved_refresh_token:
        raise EbayOAuthError(
            "eBay OAuth did not return a refresh token.",
            status_code=502,
        )

    expires_in = int(token_payload.get("expires_in", 0))
    expires_at = _utc_now() + timedelta(seconds=max(expires_in, 0))

    return EbayOAuthTokenSet(
        access_token=token_payload["access_token"],
        refresh_token=resolved_refresh_token,
        token_type=token_payload.get("token_type", "User Access Token"),
        scope=token_payload.get("scope", " ".join(DEFAULT_SCOPES)),
        expires_at=expires_at,
        environment=settings.ebay_env,
        marketplace_id=settings.ebay_marketplace_id,
    )


def _is_access_token_stale(token_set: EbayOAuthTokenSet) -> bool:
    refresh_cutoff = _utc_now() + timedelta(seconds=ACCESS_TOKEN_REFRESH_BUFFER_SECONDS)
    return token_set.expires_at <= refresh_cutoff


def get_default_scopes() -> list[str]:
    return list(DEFAULT_SCOPES)


def get_configuration_status() -> EbayConnectionStatus:
    settings = get_settings()
    token_set = get_token_set()
    connected = False
    expires_at: str | None = None

    if token_set:
        if _is_access_token_stale(token_set):
            try:
                token_set = refresh_user_access_token()
                connected = True
                expires_at = token_set.expires_at.isoformat()
            except EbayOAuthError:
                connected = False
                expires_at = token_set.expires_at.isoformat()
        else:
            connected = True
            expires_at = token_set.expires_at.isoformat()

    return EbayConnectionStatus(
        configured=_is_configured(),
        connected=connected,
        environment=settings.ebay_env,
        marketplaceId=settings.ebay_marketplace_id,
        scope=(token_set.scope.split() if token_set else get_default_scopes()),
        expiresAt=expires_at,
    )


def build_authorization_url() -> str:
    _require_configuration()
    settings = get_settings()

    state = token_urlsafe(24)
    save_pending_state(
        state,
        _utc_now() + timedelta(minutes=STATE_TTL_MINUTES),
    )

    query = urlencode(
        {
            "client_id": settings.ebay_client_id,
            "redirect_uri": settings.ebay_redirect_uri,
            "response_type": "code",
            "scope": " ".join(DEFAULT_SCOPES),
            "state": state,
        }
    )
    return f"{_get_authorization_endpoint()}?{query}"


def exchange_authorization_code(code: str, state: str) -> EbayOAuthTokenSet:
    _require_configuration()

    if not consume_pending_state(state):
        raise EbayOAuthError(
            "The eBay OAuth state value is missing or expired. Start the connection flow again.",
            status_code=400,
        )

    settings = get_settings()
    token_payload = _exchange_token_request(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.ebay_redirect_uri,
        }
    )
    return save_token_set(_build_token_set(token_payload))


def refresh_user_access_token() -> EbayOAuthTokenSet:
    _require_configuration()
    existing_token_set = get_token_set()
    if not existing_token_set:
        raise EbayOAuthError(
            "No eBay refresh token is stored on the backend.",
            status_code=400,
        )

    token_payload = _exchange_token_request(
        {
            "grant_type": "refresh_token",
            "refresh_token": existing_token_set.refresh_token,
        }
    )
    return save_token_set(
        _build_token_set(token_payload, refresh_token=existing_token_set.refresh_token)
    )


def get_valid_access_token() -> str:
    token_set = get_token_set()
    if not token_set:
        raise EbayOAuthError(
            "No eBay OAuth connection is stored on the backend.",
            status_code=400,
        )

    if _is_access_token_stale(token_set):
        token_set = refresh_user_access_token()

    return token_set.access_token
