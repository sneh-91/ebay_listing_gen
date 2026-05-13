from typing import Literal

from pydantic import BaseModel, Field


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
    draft_id: str = Field(alias="draftId")
    detected_item: str = Field(alias="detectedItem")
    confidence: str
    title: str
    subtitle: str
    category_suggestion: str = Field(alias="categorySuggestion")
    condition: ConditionValue
    condition_description: str = Field(alias="conditionDescription")
    description: str
    item_specifics: list[ItemSpecific] = Field(alias="itemSpecifics")
    price_suggestion: PriceSuggestion = Field(alias="priceSuggestion")
    shipping_notes: list[str] = Field(alias="shippingNotes")
    search_keywords: list[str] = Field(alias="searchKeywords")
    buyer_questions: list[BuyerQuestion] = Field(alias="buyerQuestions")
    missing_info_warnings: list[str] = Field(alias="missingInfoWarnings")

    model_config = {"populate_by_name": True}
