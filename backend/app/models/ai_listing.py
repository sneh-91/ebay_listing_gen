from typing import Literal

from pydantic import BaseModel, Field


ConditionValue = Literal["New", "Like New", "Used", "For parts/not working"]


class AIItemSpecific(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    value: str = Field(min_length=1, max_length=160)


class AIPriceSuggestion(BaseModel):
    amount: str = Field(min_length=1, max_length=32)
    currency: str = Field(min_length=3, max_length=3)
    confidence: str = Field(min_length=1, max_length=32)
    rationale: str = Field(min_length=1, max_length=280)


class AIBuyerQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=140)
    answer: str = Field(min_length=1, max_length=220)


class AIListingDraft(BaseModel):
    detectedItem: str = Field(min_length=1, max_length=120)
    confidence: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=80)
    subtitle: str = Field(min_length=1, max_length=80)
    categorySuggestion: str = Field(min_length=1, max_length=120)
    condition: ConditionValue
    conditionDescription: str = Field(min_length=1, max_length=220)
    description: str = Field(min_length=1, max_length=1500)
    itemSpecifics: list[AIItemSpecific] = Field(min_length=1, max_length=8)
    priceSuggestion: AIPriceSuggestion
    shippingNotes: list[str] = Field(min_length=1, max_length=4)
    searchKeywords: list[str] = Field(min_length=1, max_length=8)
    buyerQuestions: list[AIBuyerQuestion] = Field(min_length=1, max_length=4)
    missingInfoWarnings: list[str] = Field(min_length=1, max_length=5)
