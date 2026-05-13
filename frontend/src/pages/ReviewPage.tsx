import { useEffect, useMemo, useState } from "react";
import { ApiError } from "../api/client";
import { getListingDraft, updateListingDraft } from "../api/listings";
import { BuyerQuestionsCard } from "../components/BuyerQuestionsCard";
import { EditableField } from "../components/EditableField";
import { PriceSuggestionCard } from "../components/PriceSuggestionCard";
import { WarningBanner } from "../components/WarningBanner";
import type {
  DraftUpdatePayload,
  ItemSpecific,
  ListingCondition,
  ListingDraft,
} from "../types/listing";

type ReviewPageProps = {
  draftId: string;
  onBackToCreate: () => void;
  onNavigateHome: () => void;
};

type ReviewDraftState = DraftUpdatePayload;

type StoredPreviewImage = {
  id: string;
  previewUrl: string;
  name: string;
};

const conditionOptions: Exclude<ListingCondition, "">[] = [
  "New",
  "Like New",
  "Used",
  "For parts/not working",
];

function buildEditableState(draft: ListingDraft): ReviewDraftState {
  return {
    title: draft.title,
    categorySuggestion: draft.categorySuggestion,
    condition: draft.condition,
    description: draft.description,
    itemSpecifics: draft.itemSpecifics,
    priceSuggestion: {
      amount: draft.priceSuggestion.amount,
      rationale: draft.priceSuggestion.rationale,
    },
  };
}

function getStoredPreviewImages(draftId: string): StoredPreviewImage[] {
  const rawValue = window.sessionStorage.getItem(`listing-draft:${draftId}`);

  if (!rawValue) {
    return [];
  }

  try {
    const parsed = JSON.parse(rawValue) as { previewImages?: StoredPreviewImage[] };
    return parsed.previewImages ?? [];
  } catch {
    return [];
  }
}

function parseItemSpecifics(text: string): ItemSpecific[] {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const separatorIndex = line.indexOf(":");
      if (separatorIndex === -1) {
        return { name: line, value: "Needs confirmation" };
      }

      return {
        name: line.slice(0, separatorIndex).trim(),
        value: line.slice(separatorIndex + 1).trim() || "Needs confirmation",
      };
    });
}

function stringifyItemSpecifics(itemSpecifics: ItemSpecific[]): string {
  return itemSpecifics.map((item) => `${item.name}: ${item.value}`).join("\n");
}

export function ReviewPage({
  draftId,
  onBackToCreate,
  onNavigateHome,
}: ReviewPageProps) {
  const [draft, setDraft] = useState<ListingDraft | null>(null);
  const [formState, setFormState] = useState<ReviewDraftState | null>(null);
  const [itemSpecificsText, setItemSpecificsText] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const previewImages = useMemo(() => getStoredPreviewImages(draftId), [draftId]);

  useEffect(() => {
    let isActive = true;

    const loadDraft = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const nextDraft = await getListingDraft(draftId);
        if (!isActive) {
          return;
        }
        setDraft(nextDraft);
        setFormState(buildEditableState(nextDraft));
        setItemSpecificsText(stringifyItemSpecifics(nextDraft.itemSpecifics));
      } catch (error) {
        if (!isActive) {
          return;
        }
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load the listing draft.";
        setErrorMessage(message);
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    void loadDraft();

    return () => {
      isActive = false;
    };
  }, [draftId]);

  const setField = <Key extends keyof ReviewDraftState>(
    field: Key,
    value: ReviewDraftState[Key],
  ) => {
    setFormState((currentState) =>
      currentState
        ? {
            ...currentState,
            [field]: value,
          }
        : currentState,
    );
    setStatusMessage(null);
  };

  const handleSave = async () => {
    if (!formState) {
      return;
    }

    const payload: DraftUpdatePayload = {
      ...formState,
      itemSpecifics: parseItemSpecifics(itemSpecificsText),
    };

    setIsSaving(true);
    setErrorMessage(null);
    setStatusMessage(null);

    try {
      const updatedDraft = await updateListingDraft(draftId, payload);
      setDraft(updatedDraft);
      setFormState(buildEditableState(updatedDraft));
      setItemSpecificsText(stringifyItemSpecifics(updatedDraft.itemSpecifics));
      setStatusMessage("Draft saved.");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to save draft changes.";
      setErrorMessage(message);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-hero px-4 py-6 text-text">
        <div className="mx-auto max-w-4xl rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
          <p className="text-sm uppercase tracking-[0.25em] text-muted">
            Loading Draft
          </p>
          <p className="mt-3 text-lg text-text">Fetching saved review data...</p>
        </div>
      </main>
    );
  }

  if (!draft || !formState) {
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
          <h1 className="mt-4 text-3xl font-semibold text-text">Draft not found</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
            {errorMessage || "The requested draft could not be loaded."}
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
            <h1 className="mt-3 text-3xl font-semibold text-text">Review listing draft</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              Draft ID: {draft.draftId} | Confidence: {draft.confidence}
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:items-end">
            <button
              type="button"
              className="rounded-2xl bg-accentStrong px-5 py-3 text-sm font-medium text-slate-950 transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? "Saving draft..." : "Save Draft"}
            </button>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="rounded-2xl border border-border bg-surfaceAlt/80 px-4 py-3 text-sm font-medium text-text opacity-70"
                disabled
              >
                Regenerate Draft
              </button>
              <button
                type="button"
                className="rounded-2xl border border-border bg-surfaceAlt/80 px-4 py-3 text-sm font-medium text-text opacity-70"
                disabled
              >
                Create eBay Sandbox Listing
              </button>
            </div>
          </div>
        </div>

        {errorMessage ? (
          <p className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
            {errorMessage}
          </p>
        ) : null}

        {statusMessage ? (
          <p className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-50">
            {statusMessage}
          </p>
        ) : null}

        <WarningBanner warnings={draft.missingInfoWarnings} />

        {previewImages.length > 0 ? (
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
                  <p className="truncate px-4 py-3 text-sm text-muted">{image.name}</p>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6 rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
            <div>
              <p className="text-sm uppercase tracking-[0.25em] text-muted">Core Draft</p>
              <p className="mt-2 text-sm leading-6 text-muted">
                Detected item: {draft.detectedItem}
              </p>
              <p className="mt-1 text-sm leading-6 text-muted">
                Subtitle: {draft.subtitle}
              </p>
            </div>

            <EditableField label="Title">
              <input
                type="text"
                value={formState.title}
                className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                onChange={(event) => setField("title", event.target.value)}
              />
            </EditableField>

            <div className="grid gap-4 sm:grid-cols-2">
              <EditableField label="Category suggestion">
                <input
                  type="text"
                  value={formState.categorySuggestion}
                  className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                  onChange={(event) =>
                    setField("categorySuggestion", event.target.value)
                  }
                />
              </EditableField>

              <EditableField label="Condition" hint={draft.conditionDescription}>
                <select
                  value={formState.condition}
                  className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                  onChange={(event) =>
                    setField("condition", event.target.value as DraftUpdatePayload["condition"])
                  }
                >
                  {conditionOptions.map((condition) => (
                    <option key={condition} value={condition}>
                      {condition}
                    </option>
                  ))}
                </select>
              </EditableField>
            </div>

            <EditableField label="Description">
              <textarea
                rows={8}
                value={formState.description}
                className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                onChange={(event) => setField("description", event.target.value)}
              />
            </EditableField>

            <EditableField
              label="Item specifics"
              hint="Edit one specific per line using Name: Value format."
            >
              <textarea
                rows={7}
                value={itemSpecificsText}
                className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                onChange={(event) => {
                  setItemSpecificsText(event.target.value);
                  setStatusMessage(null);
                }}
              />
            </EditableField>
          </div>

          <div className="space-y-6">
            <PriceSuggestionCard
              amount={formState.priceSuggestion.amount}
              currency={draft.priceSuggestion.currency}
              confidence={draft.priceSuggestion.confidence}
              rationale={formState.priceSuggestion.rationale}
              onAmountChange={(value) =>
                setField("priceSuggestion", {
                  ...formState.priceSuggestion,
                  amount: value,
                })
              }
              onRationaleChange={(value) =>
                setField("priceSuggestion", {
                  ...formState.priceSuggestion,
                  rationale: value,
                })
              }
            />

            <StaticListCard title="Shipping notes" items={draft.shippingNotes} />
            <StaticListCard title="Search keywords" items={draft.searchKeywords} />
            <BuyerQuestionsCard questions={draft.buyerQuestions} />
          </div>
        </section>
      </div>
    </main>
  );
}

type StaticListCardProps = {
  title: string;
  items: string[];
};

function StaticListCard({ title, items }: StaticListCardProps) {
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
