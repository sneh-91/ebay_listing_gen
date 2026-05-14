import { useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { getEbayCategoryStatus, getEbaySetupStatus } from "../api/ebay";
import { getListingDraft, updateListingDraft } from "../api/listings";
import { BuyerQuestionsCard } from "../components/BuyerQuestionsCard";
import { EditableField } from "../components/EditableField";
import { PriceSuggestionCard } from "../components/PriceSuggestionCard";
import { WarningBanner } from "../components/WarningBanner";
import type {
  EbayAspectRequirement,
  EbayCategoryOption,
  EbayCategoryStatus,
  EbayLocationOption,
  EbayPolicyOption,
  EbaySetupStatus,
} from "../types/ebay";
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

const conditionOptions: Exclude<ListingCondition, "">[] = [
  "New",
  "Like New",
  "Used",
  "For parts/not working",
];

function buildEditableState(draft: ListingDraft): ReviewDraftState {
  return {
    title: draft.title,
    categoryText: draft.categoryText,
    condition: draft.condition,
    description: draft.description,
    itemSpecifics: draft.itemSpecifics,
    price: draft.price,
    quantity: draft.quantity,
    merchantLocationKey: draft.merchantLocationKey,
    paymentPolicyId: draft.paymentPolicyId,
    fulfillmentPolicyId: draft.fulfillmentPolicyId,
    returnPolicyId: draft.returnPolicyId,
    priceSuggestion: {
      rationale: draft.priceSuggestion.rationale,
    },
  };
}

function applySetupSelections(
  draft: ListingDraft,
  setupStatus: EbaySetupStatus,
): ListingDraft {
  return {
    ...draft,
    merchantLocationKey: setupStatus.selections.merchantLocationKey,
    paymentPolicyId: setupStatus.selections.paymentPolicyId,
    fulfillmentPolicyId: setupStatus.selections.fulfillmentPolicyId,
    returnPolicyId: setupStatus.selections.returnPolicyId,
  };
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
  const [setupStatus, setSetupStatus] = useState<EbaySetupStatus | null>(null);
  const [setupError, setSetupError] = useState<string | null>(null);
  const [isLoadingSetup, setIsLoadingSetup] = useState(false);
  const [categoryStatus, setCategoryStatus] = useState<EbayCategoryStatus | null>(null);
  const [categoryError, setCategoryError] = useState<string | null>(null);
  const [isLoadingCategory, setIsLoadingCategory] = useState(false);

  useEffect(() => {
    let isActive = true;

    const loadSetupStatus = async (baseDraft: ListingDraft) => {
      setIsLoadingSetup(true);
      setSetupError(null);

      try {
        const nextSetupStatus = await getEbaySetupStatus(draftId);
        if (!isActive) {
          return;
        }
        const syncedDraft = applySetupSelections(baseDraft, nextSetupStatus);
        setSetupStatus(nextSetupStatus);
        setDraft(syncedDraft);
        setFormState(buildEditableState(syncedDraft));
      } catch (error) {
        if (!isActive) {
          return;
        }
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load eBay setup status.";
        setSetupError(message);
      } finally {
        if (isActive) {
          setIsLoadingSetup(false);
        }
      }
    };

    const loadCategoryStatus = async (baseDraft: ListingDraft) => {
      setIsLoadingCategory(true);
      setCategoryError(null);

      try {
        const nextCategoryStatus = await getEbayCategoryStatus(draftId);
        if (!isActive) {
          return;
        }
        const syncedDraft = {
          ...baseDraft,
          categoryText: nextCategoryStatus.selectedCategoryLabel || baseDraft.categoryText,
          categorySuggestion:
            nextCategoryStatus.selectedCategoryLabel || baseDraft.categorySuggestion,
          categoryId: nextCategoryStatus.categoryId,
        };
        setCategoryStatus(nextCategoryStatus);
        setDraft((currentDraft) =>
          currentDraft
            ? {
                ...currentDraft,
                categoryText: syncedDraft.categoryText,
                categorySuggestion: syncedDraft.categorySuggestion,
                categoryId: syncedDraft.categoryId,
              }
            : syncedDraft,
        );
        setFormState((currentState) =>
          currentState
            ? {
                ...currentState,
                categoryText: syncedDraft.categoryText,
              }
            : buildEditableState(syncedDraft),
        );
      } catch (error) {
        if (!isActive) {
          return;
        }
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to load category requirements.";
        setCategoryError(message);
      } finally {
        if (isActive) {
          setIsLoadingCategory(false);
        }
      }
    };

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
        void loadSetupStatus(nextDraft);
        void loadCategoryStatus(nextDraft);
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
      let nextDraft = updatedDraft;
      try {
        const nextSetupStatus = await getEbaySetupStatus(draftId);
        setSetupStatus(nextSetupStatus);
        nextDraft = applySetupSelections(updatedDraft, nextSetupStatus);
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to refresh eBay setup status.";
        setSetupError(message);
      }
      try {
        const nextCategoryStatus = await getEbayCategoryStatus(draftId);
        setCategoryStatus(nextCategoryStatus);
        nextDraft = {
          ...nextDraft,
          categoryText: nextCategoryStatus.selectedCategoryLabel || nextDraft.categoryText,
          categorySuggestion:
            nextCategoryStatus.selectedCategoryLabel || nextDraft.categorySuggestion,
          categoryId: nextCategoryStatus.categoryId,
        };
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : "Unable to refresh category requirements.";
        setCategoryError(message);
      }
      setDraft(nextDraft);
      setFormState(buildEditableState(nextDraft));
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

        {draft.imageUrls.length > 0 ? (
          <section className="rounded-[1.75rem] border border-white/10 bg-surface/70 p-6">
            <p className="text-sm uppercase tracking-[0.25em] text-muted">
              Uploaded Images
            </p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {draft.imageUrls.map((imageUrl, index) => (
                <article
                  key={imageUrl}
                  className="overflow-hidden rounded-[1.5rem] border border-white/8 bg-surfaceAlt/70"
                >
                  <div className="aspect-[4/3] overflow-hidden bg-background">
                    <img
                      src={imageUrl}
                      alt={`Uploaded image ${index + 1}`}
                      className="h-full w-full object-cover"
                    />
                  </div>
                  <p className="truncate px-4 py-3 text-sm text-muted">
                    Uploaded image {index + 1}
                  </p>
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
              <p className="mt-1 text-sm leading-6 text-muted">
                Publish status: {draft.publishStatus}
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
                <select
                  value={formState.categoryText}
                  className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
                  onChange={(event) => setField("categoryText", event.target.value)}
                >
                  {(categoryStatus?.options || []).map((option) => (
                    <option key={option.key} value={option.label}>
                      {option.label}
                    </option>
                  ))}
                </select>
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
            <PublishDetailsCard draft={draft} />
            <CategoryStatusCard
              categoryStatus={categoryStatus}
              categoryError={categoryError}
              isLoadingCategory={isLoadingCategory}
            />
            <EbaySetupCard
              setupStatus={setupStatus}
              setupError={setupError}
              isLoadingSetup={isLoadingSetup}
              values={formState}
              onChange={setField}
            />
            <PriceSuggestionCard
              price={formState.price}
              quantity={formState.quantity}
              currency={draft.currency}
              confidence={draft.priceSuggestion.confidence}
              rationale={formState.priceSuggestion.rationale}
              onPriceChange={(value) => setField("price", value)}
              onQuantityChange={(value) => setField("quantity", value)}
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

type CategoryStatusCardProps = {
  categoryStatus: EbayCategoryStatus | null;
  categoryError: string | null;
  isLoadingCategory: boolean;
};

function CategoryStatusCard({
  categoryStatus,
  categoryError,
  isLoadingCategory,
}: CategoryStatusCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        Category Requirements
      </p>
      <p className="mt-2 text-sm text-muted">
        Category ID: {categoryStatus?.categoryId || "Pending resolution"}
      </p>

      {isLoadingCategory ? (
        <p className="mt-4 rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3 text-sm text-muted">
          Checking supported category and required specifics...
        </p>
      ) : null}

      {categoryError ? (
        <p className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {categoryError}
        </p>
      ) : null}

      {categoryStatus?.blockers.length ? (
        <div className="mt-4 space-y-3">
          {categoryStatus.blockers.map((blocker) => (
            <p
              key={blocker.code}
              className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100"
            >
              {blocker.message}
            </p>
          ))}
        </div>
      ) : null}

      {categoryStatus?.warnings.length ? (
        <div className="mt-4 space-y-3">
          {categoryStatus.warnings.map((warning) => (
            <p
              key={warning.code}
              className="rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-50"
            >
              {warning.message}
            </p>
          ))}
        </div>
      ) : null}

      {categoryStatus?.requiredAspects.length ? (
        <div className="mt-5 space-y-3">
          {categoryStatus.requiredAspects.map((aspect) => (
            <AspectRow key={aspect.name} aspect={aspect} />
          ))}
        </div>
      ) : null}
    </section>
  );
}

type AspectRowProps = {
  aspect: EbayAspectRequirement;
};

function AspectRow({ aspect }: AspectRowProps) {
  return (
    <div className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3 text-sm text-slate-200">
      <p className="font-medium">{aspect.name}</p>
      <p className="mt-1 text-muted">
        {aspect.satisfied
          ? `Current value: ${aspect.currentValue}`
          : "Missing or unresolved in item specifics"}
      </p>
    </div>
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

type PublishDetailsCardProps = {
  draft: ListingDraft;
};

function PublishDetailsCard({ draft }: PublishDetailsCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        Publish Fields
      </p>
      <div className="mt-4 space-y-3 text-sm text-slate-200">
        <p className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3">
          Category ID: {draft.categoryId || "Pending category resolution"}
        </p>
        <p className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3">
          Merchant location: {draft.merchantLocationKey || "Pending setup"}
        </p>
        <p className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3">
          Payment policy: {draft.paymentPolicyId || "Pending setup"}
        </p>
        <p className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3">
          Fulfillment policy: {draft.fulfillmentPolicyId || "Pending setup"}
        </p>
        <p className="rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3">
          Return policy: {draft.returnPolicyId || "Pending setup"}
        </p>
      </div>
    </section>
  );
}

type EbaySetupCardProps = {
  setupStatus: EbaySetupStatus | null;
  setupError: string | null;
  isLoadingSetup: boolean;
  values: ReviewDraftState;
  onChange: <Key extends keyof ReviewDraftState>(
    field: Key,
    value: ReviewDraftState[Key],
  ) => void;
};

function EbaySetupCard({
  setupStatus,
  setupError,
  isLoadingSetup,
  values,
  onChange,
}: EbaySetupCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        eBay Setup
      </p>
      <p className="mt-2 text-sm text-muted">
        Marketplace: {setupStatus?.marketplaceId || "EBAY_CA"}
      </p>

      {isLoadingSetup ? (
        <p className="mt-4 rounded-2xl border border-white/8 bg-surfaceAlt/70 px-4 py-3 text-sm text-muted">
          Checking seller setup...
        </p>
      ) : null}

      {setupError ? (
        <p className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {setupError}
        </p>
      ) : null}

      {setupStatus?.blockers.length ? (
        <div className="mt-4 space-y-3">
          {setupStatus.blockers.map((blocker) => (
            <p
              key={blocker.code}
              className="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100"
            >
              {blocker.message}
            </p>
          ))}
        </div>
      ) : null}

      {setupStatus?.warnings.length ? (
        <div className="mt-4 space-y-3">
          {setupStatus.warnings.map((warning) => (
            <p
              key={warning.code}
              className="rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-50"
            >
              {warning.message}
            </p>
          ))}
        </div>
      ) : null}

      {setupStatus ? (
        <div className="mt-5 space-y-4">
          <PolicySelect
            label="Payment policy"
            value={values.paymentPolicyId}
            options={setupStatus.paymentPolicies}
            placeholder="Choose a payment policy"
            onChange={(value) => onChange("paymentPolicyId", value)}
          />
          <PolicySelect
            label="Fulfillment policy"
            value={values.fulfillmentPolicyId}
            options={setupStatus.fulfillmentPolicies}
            placeholder="Choose a fulfillment policy"
            onChange={(value) => onChange("fulfillmentPolicyId", value)}
          />
          <PolicySelect
            label="Return policy"
            value={values.returnPolicyId}
            options={setupStatus.returnPolicies}
            placeholder="Choose a return policy"
            onChange={(value) => onChange("returnPolicyId", value)}
          />
          <LocationSelect
            value={values.merchantLocationKey}
            options={setupStatus.merchantLocations}
            onChange={(value) => onChange("merchantLocationKey", value)}
          />
          <p className="text-xs text-muted">
            Save the draft after changing setup selections.
          </p>
        </div>
      ) : null}
    </section>
  );
}

type PolicySelectProps = {
  label: string;
  value: string | null;
  options: EbayPolicyOption[];
  placeholder: string;
  onChange: (value: string | null) => void;
};

function PolicySelect({
  label,
  value,
  options,
  placeholder,
  onChange,
}: PolicySelectProps) {
  return (
    <EditableField label={label}>
      <select
        value={value || ""}
        className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
        onChange={(event) => onChange(event.target.value || null)}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
            {option.isDefault ? " (Default)" : ""}
          </option>
        ))}
      </select>
    </EditableField>
  );
}

type LocationSelectProps = {
  value: string | null;
  options: EbayLocationOption[];
  onChange: (value: string | null) => void;
};

function LocationSelect({ value, options, onChange }: LocationSelectProps) {
  return (
    <EditableField label="Merchant location">
      <select
        value={value || ""}
        className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
        onChange={(event) => onChange(event.target.value || null)}
      >
        <option value="">Choose a merchant location</option>
        {options.map((option) => (
          <option key={option.merchantLocationKey} value={option.merchantLocationKey}>
            {option.name}
            {option.city ? ` - ${option.city}` : ""}
            {option.country ? `, ${option.country}` : ""}
          </option>
        ))}
      </select>
    </EditableField>
  );
}
