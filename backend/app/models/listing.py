from typing import Literal

from pydantic import BaseModel, Field


ConditionValue = Literal["New", "Like New", "Used", "For parts/not working"]
PublishStatusValue = Literal["draft", "published", "publish_failed"]


class ItemSpecific(BaseModel):
    name: str
    value: str


class PriceSuggestion(BaseModel):
    amount: str
    currency: str = "CAD"
    confidence: str
    rationale: str


class BuyerQuestion(BaseModel):
    question: str
    answer: str


class ListingDraft(BaseModel):
    draftId: str
    detectedItem: str
    confidence: str
    title: str
    subtitle: str
    categorySuggestion: str
    categoryText: str
    categoryId: str | None = None
    condition: ConditionValue
    conditionDescription: str
    description: str
    itemSpecifics: list[ItemSpecific]
    price: str
    currency: str = "CAD"
    quantity: int = 1
    priceSuggestion: PriceSuggestion
    shippingNotes: list[str]
    searchKeywords: list[str]
    buyerQuestions: list[BuyerQuestion]
    missingInfoWarnings: list[str]
    imageUrls: list[str] = Field(default_factory=list)
    merchantLocationKey: str | None = None
    paymentPolicyId: str | None = None
    fulfillmentPolicyId: str | None = None
    returnPolicyId: str | None = None
    publishStatus: PublishStatusValue = "draft"
    sku: str | None = None
    offerId: str | None = None
    listingId: str | None = None
    listingUrl: str | None = None
