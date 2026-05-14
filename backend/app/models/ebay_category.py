from pydantic import BaseModel, Field

from app.models.ebay_setup import EbaySetupMessage


class EbayCategoryOption(BaseModel):
    key: str
    label: str
    categoryId: str


class EbayAspectRequirement(BaseModel):
    name: str
    required: bool
    currentValue: str | None = None
    satisfied: bool


class EbayCategoryStatus(BaseModel):
    resolved: bool
    selectedCategoryKey: str | None = None
    selectedCategoryLabel: str | None = None
    categoryId: str | None = None
    blockers: list[EbaySetupMessage] = Field(default_factory=list)
    warnings: list[EbaySetupMessage] = Field(default_factory=list)
    options: list[EbayCategoryOption] = Field(default_factory=list)
    requiredAspects: list[EbayAspectRequirement] = Field(default_factory=list)
    missingRequiredAspects: list[str] = Field(default_factory=list)
