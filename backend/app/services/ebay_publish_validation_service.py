import re

from app.models.ebay_publish import PublishValidationIssue
from app.models.listing import ListingDraft
from app.services.ebay_setup_service import get_setup_status
from app.services.ebay_taxonomy_service import get_category_status

MONEY_PATTERN = re.compile(r"^\d+(?:\.\d{2})$")


def validate_publishable_draft(session_id: str, draft: ListingDraft) -> list[PublishValidationIssue]:
    issues: list[PublishValidationIssue] = []

    if not draft.title.strip():
        issues.append(PublishValidationIssue(field="title", message="Title is required."))
    if not draft.description.strip():
        issues.append(PublishValidationIssue(field="description", message="Description is required."))
    if not draft.categoryId:
        issues.append(PublishValidationIssue(field="categoryId", message="A supported category must be selected."))
    if not draft.categoryText.strip():
        issues.append(PublishValidationIssue(field="categoryText", message="Category selection is required."))
    if not MONEY_PATTERN.fullmatch(draft.price.strip()):
        issues.append(
            PublishValidationIssue(
                field="price",
                message="Price must be a positive amount with two decimal places.",
            )
        )
    if draft.quantity < 1:
        issues.append(PublishValidationIssue(field="quantity", message="Quantity must be at least 1."))
    if not draft.imageUrls:
        issues.append(PublishValidationIssue(field="imageUrls", message="At least one image URL is required."))
    elif any(not image_url.startswith("https://") for image_url in draft.imageUrls):
        issues.append(PublishValidationIssue(field="imageUrls", message="All image URLs must use HTTPS."))

    setup_status = get_setup_status(session_id, draft)
    for blocker in setup_status.blockers:
        field = {
            "payment_policy_missing": "paymentPolicyId",
            "payment_policy_selection_required": "paymentPolicyId",
            "fulfillment_policy_missing": "fulfillmentPolicyId",
            "fulfillment_policy_selection_required": "fulfillmentPolicyId",
            "return_policy_missing": "returnPolicyId",
            "return_policy_selection_required": "returnPolicyId",
            "merchant_location_missing": "merchantLocationKey",
            "merchant_location_selection_required": "merchantLocationKey",
            "oauth_reconnect_required": "oauth",
            "oauth_not_connected": "oauth",
            "oauth_not_configured": "oauth",
            "oauth_token_invalid": "oauth",
            "draft_images_missing": "imageUrls",
            "draft_images_not_https": "imageUrls",
        }.get(blocker.code, "setup")
        issues.append(PublishValidationIssue(field=field, message=blocker.message))

    category_status = get_category_status(session_id, draft)
    for blocker in category_status.blockers:
        if blocker.code == "required_aspects_missing":
            continue
        issues.append(PublishValidationIssue(field="categoryId", message=blocker.message))
    for aspect_name in category_status.missingRequiredAspects:
        issues.append(
            PublishValidationIssue(
                field=f"itemSpecifics.{aspect_name}",
                message=f'Required item specific "{aspect_name}" is missing or unresolved.',
            )
        )

    deduped: dict[tuple[str, str], PublishValidationIssue] = {}
    for issue in issues:
        deduped[(issue.field, issue.message)] = issue
    return list(deduped.values())
