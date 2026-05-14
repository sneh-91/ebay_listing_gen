from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class EbayOAuthStartResponse(BaseModel):
    authorizationUrl: str


class EbayOAuthTokenSet(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    scope: str
    expires_at: datetime
    environment: Literal["sandbox", "production"]
    marketplace_id: str


class EbayConnectionStatus(BaseModel):
    configured: bool
    connected: bool
    environment: Literal["sandbox", "production"]
    marketplaceId: str
    scope: list[str]
    expiresAt: str | None = None
