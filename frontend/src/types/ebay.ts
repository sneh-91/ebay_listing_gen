export type EbayConnectionStatus = {
  configured: boolean;
  connected: boolean;
  requiresReconnect: boolean;
  environment: "sandbox" | "production";
  marketplaceId: string;
  scope: string[];
  missingScopes: string[];
  expiresAt: string | null;
};

export type EbayOAuthStartResponse = {
  authorizationUrl: string;
};
