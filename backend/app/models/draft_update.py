import re

from pydantic import BaseModel, field_validator

from app.models.listing import ConditionValue


MONEY_PATTERN = re.compile(r"^\d+(?:\.\d{2})$")


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
    rationale: str

    @field_validator("rationale")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Price suggestion fields cannot be blank.")
        return trimmed


class DraftUpdatePayload(BaseModel):
    title: str
    categoryText: str
    condition: ConditionValue
    description: str
    itemSpecifics: list[DraftItemSpecificUpdate]
    price: str
    quantity: int
    merchantLocationKey: str | None = None
    paymentPolicyId: str | None = None
    fulfillmentPolicyId: str | None = None
    returnPolicyId: str | None = None
    priceSuggestion: DraftPriceSuggestionUpdate

    @field_validator("title", "categoryText", "description", "price")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Draft fields cannot be blank.")
        return trimmed

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: str) -> str:
        trimmed = value.strip()
        if not MONEY_PATTERN.fullmatch(trimmed):
            raise ValueError("Price must be a positive amount with two decimal places.")
        return trimmed

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Quantity must be at least 1.")
        return value

    @field_validator(
        "merchantLocationKey",
        "paymentPolicyId",
        "fulfillmentPolicyId",
        "returnPolicyId",
    )
    @classmethod
    def normalize_optional_ids(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("itemSpecifics")
    @classmethod
    def validate_item_specifics(cls, value: list[DraftItemSpecificUpdate]) -> list[DraftItemSpecificUpdate]:
        if not value:
            raise ValueError("At least one item specific is required.")
        return value
