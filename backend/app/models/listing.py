from typing import Literal

from pydantic import BaseModel


ConditionValue = Literal["New", "Like New", "Used", "For parts/not working"]


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
    condition: ConditionValue
    conditionDescription: str
    description: str
    itemSpecifics: list[ItemSpecific]
    priceSuggestion: PriceSuggestion
    shippingNotes: list[str]
    searchKeywords: list[str]
    buyerQuestions: list[BuyerQuestion]
    missingInfoWarnings: list[str]
