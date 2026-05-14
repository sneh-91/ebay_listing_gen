import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models.listing import ListingDraft
from app.services.ebay_oauth_service import EbayOAuthError, get_valid_access_token


class EbayInventoryError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _inventory_root() -> str:
    settings = get_settings()
    if settings.ebay_env == "production":
        return "https://api.ebay.com/sell/inventory/v1"
    return "https://api.sandbox.ebay.com/sell/inventory/v1"


def _request_json(method: str, url: str, access_token: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Content-Language": "en-CA" if get_settings().ebay_marketplace_id == "EBAY_CA" else "en-US",
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw_payload = response.read().decode("utf-8")
            return json.loads(raw_payload) if raw_payload else {}
    except HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(response_text)
            errors = payload.get("errors") or []
            if errors:
                message = "; ".join(error.get("message", "eBay Inventory API error") for error in errors)
            else:
                message = payload.get("message") or payload.get("error_description") or payload.get("error")
        except json.JSONDecodeError:
            message = None
        status_code = exc.code if 400 <= exc.code < 500 else 502
        raise EbayInventoryError(
            message or "eBay Inventory API request failed.",
            status_code=status_code,
        ) from exc
    except URLError as exc:
        raise EbayInventoryError("Unable to reach eBay Inventory API from the backend.") from exc


def _map_condition(condition: str) -> str:
    mapping = {
        "New": "NEW",
        "Like New": "LIKE_NEW",
        "Used": "USED_GOOD",
        "For parts/not working": "FOR_PARTS_OR_NOT_WORKING",
    }
    return mapping.get(condition, "USED_GOOD")


def _build_aspects(draft: ListingDraft) -> dict[str, list[str]]:
    aspects: dict[str, list[str]] = {}
    for item in draft.itemSpecifics:
        name = item.name.strip()
        value = item.value.strip()
        if not name or not value or value.casefold() == "needs confirmation":
            continue
        aspects[name] = [value]
    return aspects


def _build_sku(draft: ListingDraft) -> str:
    return f"listcraft-{draft.draftId}"


def _build_offer_payload(draft: ListingDraft, sku: str) -> dict:
    return {
        "sku": sku,
        "marketplaceId": get_settings().ebay_marketplace_id,
        "format": "FIXED_PRICE",
        "availableQuantity": draft.quantity,
        "categoryId": draft.categoryId,
        "merchantLocationKey": draft.merchantLocationKey,
        "listingDescription": draft.description,
        "pricingSummary": {
            "price": {
                "value": draft.price,
                "currency": draft.currency,
            }
        },
        "listingPolicies": {
            "paymentPolicyId": draft.paymentPolicyId,
            "fulfillmentPolicyId": draft.fulfillmentPolicyId,
            "returnPolicyId": draft.returnPolicyId,
        },
    }


def create_or_replace_inventory_item(session_id: str, draft: ListingDraft) -> str:
    try:
        access_token = get_valid_access_token(session_id)
    except EbayOAuthError as exc:
        raise EbayInventoryError(str(exc)) from exc

    sku = _build_sku(draft)
    payload = {
        "availability": {
            "shipToLocationAvailability": {
                "quantity": draft.quantity,
            }
        },
        "condition": _map_condition(draft.condition),
        "conditionDescription": draft.conditionDescription,
        "product": {
            "title": draft.title,
            "description": draft.description,
            "aspects": _build_aspects(draft),
            "imageUrls": draft.imageUrls,
        },
    }
    _request_json(
        "PUT",
        f"{_inventory_root()}/inventory_item/{sku}",
        access_token,
        payload,
    )
    return sku


def create_offer(session_id: str, draft: ListingDraft, sku: str) -> str:
    try:
        access_token = get_valid_access_token(session_id)
    except EbayOAuthError as exc:
        raise EbayInventoryError(str(exc)) from exc

    response = _request_json(
        "POST",
        f"{_inventory_root()}/offer",
        access_token,
        _build_offer_payload(draft, sku),
    )
    offer_id = response.get("offerId")
    if not offer_id:
        raise EbayInventoryError("eBay did not return an offer ID.")
    return offer_id


def create_or_update_offer(session_id: str, draft: ListingDraft, sku: str) -> str:
    if not draft.offerId or draft.publishStatus == "published":
        return create_offer(session_id, draft, sku)

    try:
        access_token = get_valid_access_token(session_id)
    except EbayOAuthError as exc:
        raise EbayInventoryError(str(exc)) from exc

    _request_json(
        "PUT",
        f"{_inventory_root()}/offer/{draft.offerId}",
        access_token,
        _build_offer_payload(draft, sku),
    )
    return draft.offerId


def publish_offer(session_id: str, offer_id: str) -> dict:
    try:
        access_token = get_valid_access_token(session_id)
    except EbayOAuthError as exc:
        raise EbayInventoryError(str(exc)) from exc

    return _request_json(
        "POST",
        f"{_inventory_root()}/offer/{offer_id}/publish",
        access_token,
        None,
    )
