from pydantic import BaseModel, field_validator

from app.models.listing import ConditionValue


class DraftItemSpecificUpdate(BaseModel):
    name: str
    value: str

    @field_validator("name", "value")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Item specific fields cannot be blank.")
        return trimmed


class DraftPriceSuggestionUpdate(BaseModel):
    amount: str
    rationale: str

    @field_validator("amount", "rationale")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Price suggestion fields cannot be blank.")
        return trimmed


class DraftUpdatePayload(BaseModel):
    title: str
    categorySuggestion: str
    condition: ConditionValue
    description: str
    itemSpecifics: list[DraftItemSpecificUpdate]
    priceSuggestion: DraftPriceSuggestionUpdate

    @field_validator("title", "categorySuggestion", "description")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Draft fields cannot be blank.")
        return trimmed

    @field_validator("itemSpecifics")
    @classmethod
    def validate_item_specifics(cls, value: list[DraftItemSpecificUpdate]) -> list[DraftItemSpecificUpdate]:
        if not value:
            raise ValueError("At least one item specific is required.")
        return value
