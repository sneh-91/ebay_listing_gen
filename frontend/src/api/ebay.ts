import { apiRequest } from "./client";
import type {
  EbayCategoryStatus,
  EbayConnectionStatus,
  EbayOAuthStartResponse,
  PublishListingResult,
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

export async function getEbayCategoryStatus(draftId: string): Promise<EbayCategoryStatus> {
  return apiRequest<EbayCategoryStatus>(`/api/ebay/category/status?draftId=${encodeURIComponent(draftId)}`);
}

export async function createEbayListing(draftId: string): Promise<PublishListingResult> {
  return apiRequest<PublishListingResult>("/api/ebay/create-listing", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ draftId }),
  });
}
