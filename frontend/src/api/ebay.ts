import { apiRequest } from "./client";
import type {
  EbayConnectionStatus,
  EbayOAuthStartResponse,
  EbaySetupStatus,
} from "../types/ebay";

export async function getEbayConnectionStatus(): Promise<EbayConnectionStatus> {
  return apiRequest<EbayConnectionStatus>("/api/ebay/status");
}

export async function getEbayAuthorizationUrl(): Promise<string> {
  const response = await apiRequest<EbayOAuthStartResponse>("/api/ebay/oauth/start");
  return response.authorizationUrl;
}

export async function getEbaySetupStatus(draftId: string): Promise<EbaySetupStatus> {
  return apiRequest<EbaySetupStatus>(`/api/ebay/setup/status?draftId=${encodeURIComponent(draftId)}`);
}
