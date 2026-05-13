from uuid import uuid4

from app.models.listing import ListingDraft


def build_mock_listing_draft(
    image_count: int,
    condition: str | None,
    known_issues: str | None,
    included_accessories: str | None,
    desired_price: str | None,
    seller_notes: str | None,
) -> ListingDraft:
    resolved_condition = condition or "Used"

    specifics = [
        {"name": "Brand", "value": "Needs confirmation"},
        {"name": "Model", "value": "Needs confirmation"},
        {"name": "Photo Count", "value": str(image_count)},
    ]

    if included_accessories:
        specifics.append(
            {"name": "Included Accessories", "value": included_accessories}
        )

    warnings = [
        "Brand and model should be confirmed from the product label before publishing.",
        "Verify the final category and item specifics against the actual item.",
    ]

    if known_issues:
        warnings.append(
            "Known issues were provided by the seller and should remain visible in the final description."
        )

    if image_count < 2:
        warnings.append(
            "Add more photos if possible to improve confidence before final listing creation."
        )

    description_lines = [
        "Mock listing draft generated from uploaded product photos.",
        f"Seller-selected condition: {resolved_condition}.",
    ]

    if included_accessories:
        description_lines.append(f"Included accessories: {included_accessories}.")

    if known_issues:
        description_lines.append(f"Known issues: {known_issues}.")

    if seller_notes:
        description_lines.append(f"Seller notes: {seller_notes}.")

    rationale = (
        f"Price estimate is placeholder guidance based on a {resolved_condition.lower()} item with "
        f"{image_count} uploaded image(s)."
    )

    if desired_price:
        rationale += f" Seller target price noted: {desired_price}."

    return ListingDraft(
        draftId=f"draft-{uuid4().hex[:12]}",
        detectedItem="Consumer item from uploaded product photos",
        confidence="medium",
        title="Mock eBay listing title based on uploaded photos",
        subtitle="Review and refine before publishing",
        categorySuggestion="Consumer Electronics > Other",
        condition=resolved_condition,
        conditionDescription=(
            "Condition is currently based on seller input and should be confirmed during review."
        ),
        description=" ".join(description_lines),
        itemSpecifics=specifics,
        priceSuggestion={
            "amount": desired_price or "49.99",
            "currency": "CAD",
            "confidence": "low",
            "rationale": rationale,
        },
        shippingNotes=[
            "Package the item securely and confirm final shipping weight after packing.",
            "Choose the final shipping service after verifying dimensions.",
        ],
        searchKeywords=[
            "product listing",
            "photo based draft",
            "seller verified condition",
        ],
        buyerQuestions=[
            {
                "question": "Does the listing include everything shown in the photos?",
                "answer": "Confirm all included accessories in the final listing before publish.",
            },
            {
                "question": "Are there any functional issues?",
                "answer": known_issues
                or "No specific issues were supplied yet. Confirm during review.",
            },
        ],
        missingInfoWarnings=warnings,
    )
