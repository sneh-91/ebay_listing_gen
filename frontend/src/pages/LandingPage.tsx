import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import {
  getEbayAuthorizationUrl,
  getEbayConnectionStatus,
} from "../api/ebay";
import { LandingHero } from "../components/LandingHero";
import type { EbayConnectionStatus } from "../types/ebay";

type LandingPageProps = {
  onCreateListing: () => void;
};

export function LandingPage({ onCreateListing }: LandingPageProps) {
  const [ebayStatus, setEbayStatus] = useState<EbayConnectionStatus | null>(null);
  const [isCheckingEbayStatus, setIsCheckingEbayStatus] = useState(true);
  const [isConnectingEbay, setIsConnectingEbay] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusTone, setStatusTone] = useState<"success" | "error" | null>(null);

  useEffect(() => {
    let isActive = true;

    const params = new URLSearchParams(window.location.search);
    const ebayResult = params.get("ebay");
    const callbackMessage = params.get("message");

    if (ebayResult === "connected") {
      setStatusMessage("eBay Canada Sandbox account connected.");
      setStatusTone("success");
    } else if (ebayResult === "error") {
      setStatusMessage(
        callbackMessage || "eBay OAuth could not be completed.",
      );
      setStatusTone("error");
    }

    if (ebayResult) {
      const nextUrl = `${window.location.pathname}${window.location.hash}`;
      window.history.replaceState({}, "", nextUrl);
    }

    const loadStatus = async () => {
      setIsCheckingEbayStatus(true);

      try {
        const nextStatus = await getEbayConnectionStatus();
        if (!isActive) {
          return;
        }
        setEbayStatus(nextStatus);
        if (nextStatus.requiresReconnect) {
          setStatusMessage(
            "Reconnect eBay to grant the latest seller-account read permissions needed for setup validation.",
          );
          setStatusTone("error");
        }
      } catch (error) {
        if (!isActive) {
          return;
        }
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load eBay connection status.";
        setStatusMessage(message);
        setStatusTone("error");
      } finally {
        if (isActive) {
          setIsCheckingEbayStatus(false);
        }
      }
    };

    void loadStatus();

    return () => {
      isActive = false;
    };
  }, []);

  const handleConnectEbay = async () => {
    setIsConnectingEbay(true);
    setStatusMessage(null);
    setStatusTone(null);

    try {
      const authorizationUrl = await getEbayAuthorizationUrl();
      window.location.assign(authorizationUrl);
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to start the eBay OAuth flow.";
      setStatusMessage(message);
      setStatusTone("error");
      setIsConnectingEbay(false);
    }
  };

  return (
    <main className="min-h-screen bg-hero px-4 py-6 text-text">
      <LandingHero
        onCreateListing={onCreateListing}
        onConnectEbay={handleConnectEbay}
        ebayStatus={ebayStatus}
        isCheckingEbayStatus={isCheckingEbayStatus}
        isConnectingEbay={isConnectingEbay}
        statusMessage={statusMessage}
        statusTone={statusTone}
      />
    </main>
  );
}
