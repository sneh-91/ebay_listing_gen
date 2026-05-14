from pydantic import BaseModel, Field


class EbaySetupMessage(BaseModel):
    code: str
    message: str


class EbayPolicyOption(BaseModel):
    id: str
    name: str
    marketplaceId: str
    isDefault: bool = False


class EbayLocationOption(BaseModel):
    merchantLocationKey: str
    name: str
    merchantLocationStatus: str
    locationTypes: list[str] = Field(default_factory=list)
    city: str | None = None
    country: str | None = None
    isDefault: bool = False


class EbaySetupSelections(BaseModel):
    paymentPolicyId: str | None = None
    fulfillmentPolicyId: str | None = None
    returnPolicyId: str | None = None
    merchantLocationKey: str | None = None


class EbaySetupStatus(BaseModel):
    connected: bool
    ready: bool
    marketplaceId: str
    blockers: list[EbaySetupMessage] = Field(default_factory=list)
    warnings: list[EbaySetupMessage] = Field(default_factory=list)
    selections: EbaySetupSelections
    paymentPolicies: list[EbayPolicyOption] = Field(default_factory=list)
    fulfillmentPolicies: list[EbayPolicyOption] = Field(default_factory=list)
    returnPolicies: list[EbayPolicyOption] = Field(default_factory=list)
    merchantLocations: list[EbayLocationOption] = Field(default_factory=list)
