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

export type EbaySetupMessage = {
  code: string;
  message: string;
};

export type EbayPolicyOption = {
  id: string;
  name: string;
  marketplaceId: string;
  isDefault: boolean;
};

export type EbayLocationOption = {
  merchantLocationKey: string;
  name: string;
  merchantLocationStatus: string;
  locationTypes: string[];
  city: string | null;
  country: string | null;
  isDefault: boolean;
};

export type EbaySetupSelections = {
  paymentPolicyId: string | null;
  fulfillmentPolicyId: string | null;
  returnPolicyId: string | null;
  merchantLocationKey: string | null;
};

export type EbaySetupStatus = {
  connected: boolean;
  ready: boolean;
  marketplaceId: string;
  blockers: EbaySetupMessage[];
  warnings: EbaySetupMessage[];
  selections: EbaySetupSelections;
  paymentPolicies: EbayPolicyOption[];
  fulfillmentPolicies: EbayPolicyOption[];
  returnPolicies: EbayPolicyOption[];
  merchantLocations: EbayLocationOption[];
};
