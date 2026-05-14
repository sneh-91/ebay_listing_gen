from pydantic import BaseModel, Field


class PublishValidationIssue(BaseModel):
    field: str
    message: str


class CreateListingRequest(BaseModel):
    draftId: str


class PublishWarning(BaseModel):
    message: str


class PublishListingResult(BaseModel):
    draftId: str
    success: bool
    environment: str
    sku: str
    offerId: str
    listingId: str | None = None
    listingUrl: str | None = None
    warnings: list[PublishWarning] = Field(default_factory=list)


class PublishValidationErrorDetail(BaseModel):
    message: str
    errors: list[PublishValidationIssue]
