import type { ListingDraft } from "../types/listing";

type ReviewPageProps = {
  draftId: string;
  onBackToCreate: () => void;
  onNavigateHome: () => void;
};

type StoredDraftPayload = {
  draft: ListingDraft;
  previewImages: Array<{
    id: string;
    previewUrl: string;
    name: string;
  }>;
};

function getStoredDraft(draftId: string): StoredDraftPayload | null {
  const rawValue = window.sessionStorage.getItem(`listing-draft:${draftId}`);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as StoredDraftPayload;
  } catch {
    return null;
  }
}

export function ReviewPage({
  draftId,
  onBackToCreate,
  onNavigateHome,
}: ReviewPageProps) {
  const storedDraft = getStoredDraft(draftId);

  if (!storedDraft) {
    return (
      <main className="min-h-screen bg-hero px-4 py-6 text-text">
        <div className="mx-auto max-w-4xl rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
          <button
            type="button"
            className="text-sm uppercase tracking-[0.22em] text-muted transition hover:text-text"
            onClick={onNavigateHome}
          >
            Back to landing page
          </button>
          <h1 className="mt-4 text-3xl font-semibold text-text">
            Draft not found
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            This temporary Phase 3 review route expects a generated draft in
            session storage. Create a new draft from the upload screen to load
            review data again.
          </p>
          <button
            type="button"
            className="mt-6 rounded-2xl bg-accentStrong px-6 py-3 text-base font-medium text-slate-950 transition hover:bg-sky-300"
            onClick={onBackToCreate}
          >
            Return to create page
          </button>
        </div>
      </main>
    );
  }

  const { draft, previewImages } = storedDraft;

  return (
    <main className="min-h-screen bg-hero px-4 py-6 text-text">
      <div className="mx-auto max-w-6xl space-y-6">
        <div className="flex flex-col gap-4 rounded-[1.75rem] border border-white/10 bg-surface/80 p-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <button
              type="button"
              className="text-sm uppercase tracking-[0.22em] text-muted transition hover:text-text"
              onClick={onBackToCreate}
            >
              Back to create page
            </button>
            <h1 className="mt-3 text-3xl font-semibold text-text">
              Mock listing draft
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              Draft ID: {draft.draftId} | Confidence: {draft.confidence}
            </p>
          </div>
          <button
            type="button"
            className="rounded-2xl border border-border bg-surfaceAlt/80 px-5 py-3 text-sm font-medium text-text transition hover:border-sky-300/60 hover:bg-surfaceAlt"
            onClick={onNavigateHome}
          >
            Landing page
          </button>
        </div>

        <section className="rounded-[1.75rem] border border-white/10 bg-surface/70 p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-muted">
            Uploaded Images
          </p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {previewImages.map((image) => (
              <article
                key={image.id}
                className="overflow-hidden rounded-[1.5rem] border border-white/8 bg-surfaceAlt/70"
              >
                <div className="aspect-[4/3] overflow-hidden bg-background">
                  <img
                    src={image.previewUrl}
                    alt={image.name}
                    className="h-full w-full object-cover"
                  />
                </div>
                <p className="truncate px-4 py-3 text-sm text-muted">
                  {image.name}
                </p>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="space-y-6 rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-muted">
                Core Draft
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-text">
                {draft.title}
              </h2>
              <p className="mt-2 text-sm text-muted">{draft.subtitle}</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <InfoCard label="Detected item" value={draft.detectedItem} />
              <InfoCard
                label="Category suggestion"
                value={draft.categorySuggestion}
              />
              <InfoCard label="Condition" value={draft.condition} />
              <InfoCard
                label="Condition detail"
                value={draft.conditionDescription}
              />
            </div>

            <div>
              <h3 className="text-lg font-medium text-text">Description</h3>
              <p className="mt-3 text-sm leading-7 text-slate-200">
                {draft.description}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-medium text-text">Item specifics</h3>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {draft.itemSpecifics.map((specific) => (
                  <InfoCard
                    key={`${specific.name}-${specific.value}`}
                    label={specific.name}
                    value={specific.value}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
              <p className="text-sm uppercase tracking-[0.25em] text-muted">
                Price Suggestion
              </p>
              <p className="mt-3 text-3xl font-semibold text-text">
                {draft.priceSuggestion.currency} {draft.priceSuggestion.amount}
              </p>
              <p className="mt-2 text-sm text-muted">
                Confidence: {draft.priceSuggestion.confidence}
              </p>
              <p className="mt-4 text-sm leading-6 text-slate-200">
                {draft.priceSuggestion.rationale}
              </p>
            </section>

            <ListCard
              title="Shipping notes"
              items={draft.shippingNotes}
            />
            <ListCard
              title="Search keywords"
              items={draft.searchKeywords}
            />
            <ListCard
              title="Missing info warnings"
              items={draft.missingInfoWarnings}
            />

            <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
              <p className="text-sm uppercase tracking-[0.25em] text-muted">
                Buyer Q&A
              </p>
              <div className="mt-4 space-y-4">
                {draft.buyerQuestions.map((question) => (
                  <article
                    key={question.question}
                    className="rounded-2xl border border-white/8 bg-surfaceAlt/70 p-4"
                  >
                    <h3 className="text-sm font-medium text-text">
                      {question.question}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-muted">
                      {question.answer}
                    </p>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </section>
      </div>
    </main>
  );
}

type InfoCardProps = {
  label: string;
  value: string;
};

function InfoCard({ label, value }: InfoCardProps) {
  return (
    <article className="rounded-2xl border border-white/8 bg-surfaceAlt/70 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className="mt-2 text-sm leading-6 text-slate-100">{value}</p>
    </article>
  );
}

type ListCardProps = {
  title: string;
  items: string[];
};

function ListCard({ title, items }: ListCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">{title}</p>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <p
            key={item}
            className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3 text-sm leading-6 text-slate-200"
          >
            {item}
          </p>
        ))}
      </div>
    </section>
  );
}
