import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models.ebay_setup import (
    EbayLocationOption,
    EbayPolicyOption,
    EbaySetupMessage,
    EbaySetupSelections,
    EbaySetupStatus,
)
from app.models.listing import ListingDraft
from app.services.ebay_oauth_service import EbayOAuthError, get_configuration_status, get_valid_access_token
from app.storage.draft_store import save_draft

SELLING_POLICY_MANAGEMENT = "SELLING_POLICY_MANAGEMENT"


@dataclass
class _ApiRoots:
    account: str
    inventory: str


class EbaySetupError(Exception):
    pass


def _get_api_roots() -> _ApiRoots:
    settings = get_settings()
    if settings.ebay_env == "production":
        return _ApiRoots(
            account="https://api.ebay.com/sell/account/v1",
            inventory="https://api.ebay.com/sell/inventory/v1",
        )
    return _ApiRoots(
        account="https://api.sandbox.ebay.com/sell/account/v1",
        inventory="https://api.sandbox.ebay.com/sell/inventory/v1",
    )


def _build_headers(access_token: str, include_content_language: bool = False) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    if include_content_language and get_settings().ebay_marketplace_id == "EBAY_CA":
        headers["Content-Language"] = "en-CA"
    return headers


def _request_json(url: str, headers: dict[str, str]) -> dict:
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=20) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(response_text)
            message = payload.get("message") or payload.get("error_description") or payload.get("error")
        except json.JSONDecodeError:
            message = None
        raise EbaySetupError(message or "eBay setup validation request failed.") from exc
    except URLError as exc:
        raise EbaySetupError("Unable to reach eBay setup services from the backend.") from exc


def _policy_is_default(policy_payload: dict) -> bool:
    category_types = policy_payload.get("categoryTypes") or []
    return any(category_type.get("default") is True for category_type in category_types)


def _to_policy_options(payload: dict, collection_key: str, id_key: str) -> list[EbayPolicyOption]:
    options: list[EbayPolicyOption] = []
    for policy in payload.get(collection_key, []) or []:
        policy_id = policy.get(id_key)
        name = policy.get("name")
        marketplace_id = policy.get("marketplaceId")
        if not policy_id or not name or not marketplace_id:
            continue
        options.append(
            EbayPolicyOption(
                id=policy_id,
                name=name,
                marketplaceId=marketplace_id,
                isDefault=_policy_is_default(policy),
            )
        )
    return options


def _to_location_options(payload: dict) -> list[EbayLocationOption]:
    options: list[EbayLocationOption] = []
    for location in payload.get("locations", []) or []:
        merchant_location_key = location.get("merchantLocationKey")
        name = location.get("name")
        status = location.get("merchantLocationStatus", "UNKNOWN")
        if not merchant_location_key or not name:
            continue
        address = (location.get("location") or {}).get("address") or {}
        options.append(
            EbayLocationOption(
                merchantLocationKey=merchant_location_key,
                name=name,
                merchantLocationStatus=status,
                locationTypes=location.get("locationTypes") or [],
                city=address.get("city"),
                country=address.get("country"),
                isDefault=False,
            )
        )
    return options


def _choose_selection(current_id: str | None, options: list, id_attr: str) -> str | None:
    if current_id and any(getattr(option, id_attr) == current_id for option in options):
        return current_id

    default_options = [option for option in options if getattr(option, "isDefault", False)]
    if len(default_options) == 1:
        return getattr(default_options[0], id_attr)

    if len(options) == 1:
        return getattr(options[0], id_attr)

    return None


def _build_policy_url(resource: str) -> str:
    roots = _get_api_roots()
    marketplace_id = get_settings().ebay_marketplace_id
    return f"{roots.account}/{resource}?{urlencode({'marketplace_id': marketplace_id})}"


def _build_location_url() -> str:
    roots = _get_api_roots()
    return f"{roots.inventory}/location"


def get_setup_status(session_id: str, draft: ListingDraft) -> EbaySetupStatus:
    config_status = get_configuration_status(session_id)
    blockers: list[EbaySetupMessage] = []
    warnings: list[EbaySetupMessage] = []

    selections = EbaySetupSelections(
        paymentPolicyId=draft.paymentPolicyId,
        fulfillmentPolicyId=draft.fulfillmentPolicyId,
        returnPolicyId=draft.returnPolicyId,
        merchantLocationKey=draft.merchantLocationKey,
    )

    if not config_status.configured:
        blockers.append(
            EbaySetupMessage(
                code="oauth_not_configured",
                message="eBay OAuth is not configured on the backend.",
            )
        )
        return EbaySetupStatus(
            connected=False,
            ready=False,
            marketplaceId=config_status.marketplaceId,
            blockers=blockers,
            warnings=warnings,
            selections=selections,
        )

    if config_status.requiresReconnect:
        blockers.append(
            EbaySetupMessage(
                code="oauth_reconnect_required",
                message="Reconnect eBay to grant the required account read permissions.",
            )
        )
        return EbaySetupStatus(
            connected=False,
            ready=False,
            marketplaceId=config_status.marketplaceId,
            blockers=blockers,
            warnings=warnings,
            selections=selections,
        )

    if not config_status.connected:
        blockers.append(
            EbaySetupMessage(
                code="oauth_not_connected",
                message="Connect an eBay seller account before validating setup.",
            )
        )
        return EbaySetupStatus(
            connected=False,
            ready=False,
            marketplaceId=config_status.marketplaceId,
            blockers=blockers,
            warnings=warnings,
            selections=selections,
        )

    try:
        access_token = get_valid_access_token(session_id)
    except EbayOAuthError as exc:
        blockers.append(
            EbaySetupMessage(
                code="oauth_token_invalid",
                message=str(exc),
            )
        )
        return EbaySetupStatus(
            connected=False,
            ready=False,
            marketplaceId=config_status.marketplaceId,
            blockers=blockers,
            warnings=warnings,
            selections=selections,
        )

    if not get_settings().ebay_marketplace_id:
        blockers.append(
            EbaySetupMessage(
                code="marketplace_missing",
                message="EBAY_MARKETPLACE_ID is missing on the backend.",
            )
        )

    payment_policies: list[EbayPolicyOption] = []
    fulfillment_policies: list[EbayPolicyOption] = []
    return_policies: list[EbayPolicyOption] = []
    merchant_locations: list[EbayLocationOption] = []

    try:
        programs_payload = _request_json(
            f"{_get_api_roots().account}/program/get_opted_in_programs",
            _build_headers(access_token),
        )
        opted_in_programs = {
            program.get("programType")
            for program in programs_payload.get("programs", []) or []
            if program.get("programType")
        }
        if SELLING_POLICY_MANAGEMENT not in opted_in_programs:
            blockers.append(
                EbaySetupMessage(
                    code="selling_policy_management_missing",
                    message="The seller account is not opted in to Selling Policy Management.",
                )
            )

        payment_policies = _to_policy_options(
            _request_json(_build_policy_url("payment_policy"), _build_headers(access_token)),
            collection_key="paymentPolicies",
            id_key="paymentPolicyId",
        )
        fulfillment_policies = _to_policy_options(
            _request_json(_build_policy_url("fulfillment_policy"), _build_headers(access_token)),
            collection_key="fulfillmentPolicies",
            id_key="fulfillmentPolicyId",
        )
        return_policies = _to_policy_options(
            _request_json(
                _build_policy_url("return_policy"),
                _build_headers(access_token, include_content_language=True),
            ),
            collection_key="returnPolicies",
            id_key="returnPolicyId",
        )
        merchant_locations = [
            option
            for option in _to_location_options(
                _request_json(_build_location_url(), _build_headers(access_token))
            )
            if option.merchantLocationStatus == "ENABLED"
        ]
    except EbaySetupError as exc:
        blockers.append(
            EbaySetupMessage(
                code="ebay_setup_request_failed",
                message=str(exc),
            )
        )

    selections.paymentPolicyId = _choose_selection(
        selections.paymentPolicyId,
        payment_policies,
        "id",
    )
    selections.fulfillmentPolicyId = _choose_selection(
        selections.fulfillmentPolicyId,
        fulfillment_policies,
        "id",
    )
    selections.returnPolicyId = _choose_selection(
        selections.returnPolicyId,
        return_policies,
        "id",
    )
    selections.merchantLocationKey = _choose_selection(
        selections.merchantLocationKey,
        merchant_locations,
        "merchantLocationKey",
    )

    if not payment_policies:
        blockers.append(
            EbaySetupMessage(
                code="payment_policy_missing",
                message="No payment policy is available for the configured marketplace.",
            )
        )
    elif not selections.paymentPolicyId:
        blockers.append(
            EbaySetupMessage(
                code="payment_policy_selection_required",
                message="Choose a payment policy before publishing.",
            )
        )

    if not fulfillment_policies:
        blockers.append(
            EbaySetupMessage(
                code="fulfillment_policy_missing",
                message="No fulfillment policy is available for the configured marketplace.",
            )
        )
    elif not selections.fulfillmentPolicyId:
        blockers.append(
            EbaySetupMessage(
                code="fulfillment_policy_selection_required",
                message="Choose a fulfillment policy before publishing.",
            )
        )

    if not return_policies:
        blockers.append(
            EbaySetupMessage(
                code="return_policy_missing",
                message="No return policy is available for the configured marketplace.",
            )
        )
    elif not selections.returnPolicyId:
        blockers.append(
            EbaySetupMessage(
                code="return_policy_selection_required",
                message="Choose a return policy before publishing.",
            )
        )

    if not merchant_locations:
        blockers.append(
            EbaySetupMessage(
                code="merchant_location_missing",
                message="No enabled merchant location is available for the seller account.",
            )
        )
    elif not selections.merchantLocationKey:
        blockers.append(
            EbaySetupMessage(
                code="merchant_location_selection_required",
                message="Choose a merchant location before publishing.",
            )
        )

    if not draft.imageUrls:
        blockers.append(
            EbaySetupMessage(
                code="draft_images_missing",
                message="The draft does not have stored image URLs ready for publishing.",
            )
        )
    elif any(not image_url.startswith("https://") for image_url in draft.imageUrls):
        blockers.append(
            EbaySetupMessage(
                code="draft_images_not_https",
                message="All draft images must use HTTPS URLs before publishing.",
            )
        )

    if (
        draft.paymentPolicyId != selections.paymentPolicyId
        or draft.fulfillmentPolicyId != selections.fulfillmentPolicyId
        or draft.returnPolicyId != selections.returnPolicyId
        or draft.merchantLocationKey != selections.merchantLocationKey
    ):
        updated_draft = draft.model_copy(
            update={
                "paymentPolicyId": selections.paymentPolicyId,
                "fulfillmentPolicyId": selections.fulfillmentPolicyId,
                "returnPolicyId": selections.returnPolicyId,
                "merchantLocationKey": selections.merchantLocationKey,
            }
        )
        save_draft(updated_draft, session_id)

    return EbaySetupStatus(
        connected=True,
        ready=not blockers,
        marketplaceId=config_status.marketplaceId,
        blockers=blockers,
        warnings=warnings,
        selections=selections,
        paymentPolicies=payment_policies,
        fulfillmentPolicies=fulfillment_policies,
        returnPolicies=return_policies,
        merchantLocations=merchant_locations,
    )
