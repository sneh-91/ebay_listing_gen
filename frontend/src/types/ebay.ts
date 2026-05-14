export type EbayConnectionStatus = {
  configured: boolean;
  connected: boolean;
  environment: "sandbox" | "production";
  marketplaceId: string;
  scope: string[];
  expiresAt: string | null;
};

export type EbayOAuthStartResponse = {
  authorizationUrl: string;
};
