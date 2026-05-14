import { apiRequest } from "./client";
import type {
  EbayConnectionStatus,
  EbayOAuthStartResponse,
} from "../types/ebay";

export async function getEbayConnectionStatus(): Promise<EbayConnectionStatus> {
  return apiRequest<EbayConnectionStatus>("/api/ebay/status");
}

export async function getEbayAuthorizationUrl(): Promise<string> {
  const response = await apiRequest<EbayOAuthStartResponse>("/api/ebay/oauth/start");
  return response.authorizationUrl;
}
