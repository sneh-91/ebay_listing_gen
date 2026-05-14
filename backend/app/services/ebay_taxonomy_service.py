import base64
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import get_settings
from app.models.ebay_category import (
    EbayAspectRequirement,
    EbayCategoryOption,
    EbayCategoryStatus,
)
from app.models.ebay_setup import EbaySetupMessage
from app.models.listing import ItemSpecific, ListingDraft
from app.storage.draft_store import save_draft

TAXONOMY_SCOPE = "https://api.ebay.com/oauth/api_scope"
APP_TOKEN_REFRESH_BUFFER_SECONDS = 60


@dataclass(frozen=True)
class SupportedCategory:
    key: str
    label: str
    category_id: str
    keywords: tuple[str, ...]


SUPPORTED_CATEGORIES: tuple[SupportedCategory, ...] = (
    SupportedCategory(
        key="books",
        label="Books",
        category_id="261186",
        keywords=("book", "novel", "paperback", "hardcover", "author", "isbn"),
    ),
    SupportedCategory(
        key="video_games",
        label="Video Games",
        category_id="139973",
        keywords=("video game", "game", "ps5", "ps4", "xbox", "nintendo", "switch"),
    ),
    SupportedCategory(
        key="lego_sets",
        label="LEGO Sets",
        category_id="19006",
        keywords=("lego", "set", "brick", "minifigure"),
    ),
    SupportedCategory(
        key="headphones",
        label="Headphones",
        category_id="112529",
        keywords=("headphone", "headphones", "earbuds", "earphone", "headset"),
    ),
)

_APP_TOKEN: str | None = None
_APP_TOKEN_EXPIRES_AT: datetime | None = None
_CATEGORY_TREE_ID_CACHE: dict[str, str] = {}


class EbayTaxonomyError(Exception):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _taxonomy_root() -> str:
    settings = get_settings()
    if settings.ebay_env == "production":
        return "https://api.ebay.com/commerce/taxonomy/v1"
    return "https://api.sandbox.ebay.com/commerce/taxonomy/v1"


def _identity_root() -> str:
    settings = get_settings()
    if settings.ebay_env == "production":
        return "https://api.ebay.com/identity/v1/oauth2/token"
    return "https://api.sandbox.ebay.com/identity/v1/oauth2/token"


def _basic_auth_header() -> str:
    settings = get_settings()
    credentials = f"{settings.ebay_client_id}:{settings.ebay_client_secret}".encode("utf-8")
    encoded = base64.b64encode(credentials).decode("ascii")
    return f"Basic {encoded}"


def _require_taxonomy_configuration() -> None:
    settings = get_settings()
    if not settings.ebay_client_id or not settings.ebay_client_secret:
        raise EbayTaxonomyError("eBay taxonomy access is not configured on the backend.")


def _request_token() -> tuple[str, datetime]:
    body = urlencode(
        {
            "grant_type": "client_credentials",
            "scope": TAXONOMY_SCOPE,
        }
    ).encode("utf-8")
    request = Request(
        _identity_root(),
        data=body,
        headers={
            "Authorization": _basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(response_text)
            message = payload.get("error_description") or payload.get("error")
        except json.JSONDecodeError:
            message = None
        raise EbayTaxonomyError(message or "Unable to create an eBay application token.") from exc
    except URLError as exc:
        raise EbayTaxonomyError("Unable to reach eBay taxonomy services from the backend.") from exc

    expires_in = int(payload.get("expires_in", 0))
    expires_at = _utc_now() + timedelta(seconds=max(expires_in, 0))
    access_token = payload.get("access_token")
    if not access_token:
        raise EbayTaxonomyError("eBay taxonomy token response did not include an access token.")
    return access_token, expires_at


def _get_application_access_token() -> str:
    global _APP_TOKEN, _APP_TOKEN_EXPIRES_AT

    _require_taxonomy_configuration()
    now = _utc_now()
    if (
        _APP_TOKEN
        and _APP_TOKEN_EXPIRES_AT
        and _APP_TOKEN_EXPIRES_AT > now + timedelta(seconds=APP_TOKEN_REFRESH_BUFFER_SECONDS)
    ):
        return _APP_TOKEN

    _APP_TOKEN, _APP_TOKEN_EXPIRES_AT = _request_token()
    return _APP_TOKEN


def _request_json(url: str) -> dict:
    access_token = _get_application_access_token()
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        method="GET",
    )
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
        raise EbayTaxonomyError(message or "eBay taxonomy request failed.") from exc
    except URLError as exc:
        raise EbayTaxonomyError("Unable to reach eBay taxonomy services from the backend.") from exc


def _get_default_category_tree_id(marketplace_id: str) -> str:
    cached = _CATEGORY_TREE_ID_CACHE.get(marketplace_id)
    if cached:
        return cached

    url = f"{_taxonomy_root()}/get_default_category_tree_id?{urlencode({'marketplace_id': marketplace_id})}"
    payload = _request_json(url)
    category_tree_id = payload.get("categoryTreeId")
    if not category_tree_id:
        raise EbayTaxonomyError("eBay taxonomy did not return a default category tree ID.")
    _CATEGORY_TREE_ID_CACHE[marketplace_id] = category_tree_id
    return category_tree_id


def _get_supported_category_by_key(key: str) -> SupportedCategory | None:
    return next((category for category in SUPPORTED_CATEGORIES if category.key == key), None)


def _get_supported_category_by_label(label: str) -> SupportedCategory | None:
    normalized = label.strip().lower()
    return next((category for category in SUPPORTED_CATEGORIES if category.label.lower() == normalized), None)


def _infer_supported_category(draft: ListingDraft) -> SupportedCategory | None:
    combined_text = " ".join(
        [
            draft.detectedItem,
            draft.title,
            draft.categorySuggestion,
            draft.categoryText,
            draft.description,
            " ".join(f"{item.name} {item.value}" for item in draft.itemSpecifics),
        ]
    ).lower()

    scored: list[tuple[int, SupportedCategory]] = []
    for category in SUPPORTED_CATEGORIES:
        score = sum(1 for keyword in category.keywords if keyword in combined_text)
        if score > 0:
            scored.append((score, category))

    if not scored:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def _normalize_item_specific_name(value: str) -> str:
    return value.strip().casefold()


def _find_specific_value(item_specifics: list[ItemSpecific], aspect_name: str) -> str | None:
    normalized_name = _normalize_item_specific_name(aspect_name)
    for item in item_specifics:
        if _normalize_item_specific_name(item.name) == normalized_name:
            value = item.value.strip()
            return value or None
    return None


def _is_specific_value_satisfied(value: str | None) -> bool:
    if value is None:
        return False
    return value.casefold() not in {"needs confirmation", "unknown", "n/a"}


def _fetch_required_aspects(category_id: str) -> list[EbayAspectRequirement]:
    tree_id = _get_default_category_tree_id(get_settings().ebay_marketplace_id)
    url = (
        f"{_taxonomy_root()}/category_tree/{tree_id}/get_item_aspects_for_category?"
        f"{urlencode({'category_id': category_id})}"
    )
    payload = _request_json(url)
    requirements: list[EbayAspectRequirement] = []
    for aspect in payload.get("aspects", []) or []:
        name = aspect.get("localizedAspectName")
        constraint = aspect.get("aspectConstraint") or {}
        required = bool(constraint.get("aspectRequired"))
        if not name or not required:
            continue
        requirements.append(
            EbayAspectRequirement(
                name=name,
                required=True,
                currentValue=None,
                satisfied=False,
            )
        )
    return requirements


def _build_options() -> list[EbayCategoryOption]:
    return [
        EbayCategoryOption(
            key=category.key,
            label=category.label,
            categoryId=category.category_id,
        )
        for category in SUPPORTED_CATEGORIES
    ]


def _resolve_supported_category(draft: ListingDraft) -> tuple[SupportedCategory | None, bool]:
    from_label = _get_supported_category_by_label(draft.categoryText)
    if from_label:
        return from_label, False

    inferred = _infer_supported_category(draft)
    if inferred:
        return inferred, True

    return None, False


def get_category_status(session_id: str, draft: ListingDraft) -> EbayCategoryStatus:
    options = _build_options()
    blockers: list[EbaySetupMessage] = []
    warnings: list[EbaySetupMessage] = []

    supported_category, was_inferred = _resolve_supported_category(draft)
    if not supported_category:
        blockers.append(
            EbaySetupMessage(
                code="unsupported_category",
                message="Choose one of the supported curated categories to continue.",
            )
        )
        return EbayCategoryStatus(
            resolved=False,
            selectedCategoryKey=None,
            selectedCategoryLabel=None,
            categoryId=None,
            blockers=blockers,
            warnings=warnings,
            options=options,
            requiredAspects=[],
            missingRequiredAspects=[],
        )

    resolved_draft = draft
    if (
        draft.categoryText != supported_category.label
        or draft.categoryId != supported_category.category_id
    ):
        resolved_draft = draft.model_copy(
            update={
                "categoryText": supported_category.label,
                "categorySuggestion": supported_category.label,
                "categoryId": supported_category.category_id,
            }
        )
        save_draft(resolved_draft, session_id)

    if was_inferred:
        warnings.append(
            EbaySetupMessage(
                code="category_inferred",
                message=f'Category was inferred as "{supported_category.label}". Review and change it if needed.',
            )
        )

    try:
        required_aspects = _fetch_required_aspects(supported_category.category_id)
    except EbayTaxonomyError as exc:
        blockers.append(
            EbaySetupMessage(
                code="taxonomy_request_failed",
                message=str(exc),
            )
        )
        return EbayCategoryStatus(
            resolved=True,
            selectedCategoryKey=supported_category.key,
            selectedCategoryLabel=supported_category.label,
            categoryId=supported_category.category_id,
            blockers=blockers,
            warnings=warnings,
            options=options,
            requiredAspects=[],
            missingRequiredAspects=[],
        )

    missing_required_aspects: list[str] = []
    aspect_requirements: list[EbayAspectRequirement] = []
    for aspect in required_aspects:
        current_value = _find_specific_value(resolved_draft.itemSpecifics, aspect.name)
        satisfied = _is_specific_value_satisfied(current_value)
        aspect_requirements.append(
            EbayAspectRequirement(
                name=aspect.name,
                required=True,
                currentValue=current_value,
                satisfied=satisfied,
            )
        )
        if not satisfied:
            missing_required_aspects.append(aspect.name)

    if missing_required_aspects:
        blockers.append(
            EbaySetupMessage(
                code="required_aspects_missing",
                message="Add values for the required item specifics shown below.",
            )
        )

    return EbayCategoryStatus(
        resolved=True,
        selectedCategoryKey=supported_category.key,
        selectedCategoryLabel=supported_category.label,
        categoryId=supported_category.category_id,
        blockers=blockers,
        warnings=warnings,
        options=options,
        requiredAspects=aspect_requirements,
        missingRequiredAspects=missing_required_aspects,
    )


def resolve_category_selection(category_text: str) -> tuple[str, str | None]:
    supported_category = _get_supported_category_by_label(category_text)
    if not supported_category:
        return category_text, None
    return supported_category.label, supported_category.category_id
