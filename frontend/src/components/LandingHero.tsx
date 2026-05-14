import type { EbayConnectionStatus } from "../types/ebay";

type LandingHeroProps = {
  onCreateListing: () => void;
  onConnectEbay: () => void;
  ebayStatus: EbayConnectionStatus | null;
  isCheckingEbayStatus: boolean;
  isConnectingEbay: boolean;
  statusMessage: string | null;
  statusTone: "success" | "error" | null;
};

export function LandingHero({
  onCreateListing,
  onConnectEbay,
  ebayStatus,
  isCheckingEbayStatus,
  isConnectingEbay,
  statusMessage,
  statusTone,
}: LandingHeroProps) {
  const ebayConnected = ebayStatus?.connected ?? false;
  const ebayConfigured = ebayStatus?.configured ?? false;
  const ebayRequiresReconnect = ebayStatus?.requiresReconnect ?? false;
  const ebayStatusLabel = isCheckingEbayStatus
    ? "Checking eBay connection"
    : ebayRequiresReconnect
      ? "eBay connection needs renewed permissions"
      : ebayConnected
      ? `Connected to eBay ${ebayStatus?.environment}`
      : ebayConfigured
        ? `Not connected to eBay ${ebayStatus?.environment}`
        : "Backend eBay OAuth not configured";

  return (
    <section className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-6xl items-center">
      <div className="grid w-full gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <div className="inline-flex items-center rounded-full border border-sky-400/25 bg-sky-400/10 px-3 py-1 text-sm text-accent">
            Sandbox-first AI listing workflow
          </div>
          <div className="space-y-4">
            <p className="text-sm uppercase tracking-[0.3em] text-muted">
              ListCraft AI
            </p>
            <h1 className="max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
              Turn product photos into eBay listings.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
              Upload item photos, review an AI-generated draft, and publish to
              eBay through a server-side OAuth flow without exposing sensitive
              credentials in the browser.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-surface/70 px-4 py-3 text-sm text-muted">
            {ebayStatusLabel}
          </div>
          {statusMessage ? (
            <p
              className={
                statusTone === "error"
                  ? "rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100"
                  : "rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-50"
              }
            >
              {statusMessage}
            </p>
          ) : null}
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              className="rounded-2xl bg-accentStrong px-6 py-3 text-base font-medium text-slate-950 transition hover:bg-sky-300"
              onClick={onCreateListing}
            >
              Create Listing
            </button>
            <button
              type="button"
              className="rounded-2xl border border-border bg-surface/80 px-6 py-3 text-base font-medium text-text transition hover:border-sky-300/60 hover:bg-surfaceAlt disabled:cursor-not-allowed disabled:opacity-60"
              onClick={onConnectEbay}
              disabled={isConnectingEbay || !ebayConfigured}
            >
              {isConnectingEbay
                ? "Redirecting to eBay..."
                : ebayConnected || ebayRequiresReconnect
                  ? "Reconnect eBay"
                  : "Connect eBay"}
            </button>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 rounded-[2rem] bg-sky-400/10 blur-3xl" />
          <div className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-surface/80 p-6 shadow-glow backdrop-blur">
            <div className="grid gap-4 sm:grid-cols-2">
              <FeatureCard
                title="Photo-first flow"
                description="Mobile-friendly upload with preview states for quick listing creation."
              />
              <FeatureCard
                title="Structured draft"
                description="Title, condition, price estimate, specifics, and buyer Q&A in one review step."
              />
              <FeatureCard
                title="Server-side AI"
                description="OpenAI calls stay in FastAPI so keys and prompts never live in the client."
              />
              <FeatureCard
                title="OAuth seller connect"
                description="Users connect their own eBay account while app credentials stay private."
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

type FeatureCardProps = {
  title: string;
  description: string;
};

function FeatureCard({ title, description }: FeatureCardProps) {
  return (
    <article className="rounded-2xl border border-white/8 bg-surfaceAlt/70 p-4">
      <h2 className="text-lg font-medium text-text">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-muted">{description}</p>
    </article>
  );
}
