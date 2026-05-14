export type ListingCondition =
  | ""
  | "New"
  | "Like New"
  | "Used"
  | "For parts/not working";

export type ListingResolvedCondition = Exclude<ListingCondition, "">;

export type UploadedImage = {
  id: string;
  file: File;
  previewUrl: string;
};

export type ListingFormValues = {
  condition: ListingCondition;
  knownIssues: string;
  includedAccessories: string;
  desiredPrice: string;
  sellerNotes: string;
};

export type ItemSpecific = {
  name: string;
  value: string;
};

export type PriceSuggestion = {
  amount: string;
  currency: string;
  confidence: string;
  rationale: string;
};

export type BuyerQuestion = {
  question: string;
  answer: string;
};

export type PublishStatus = "draft" | "published" | "publish_failed";

export type ListingDraft = {
  draftId: string;
  detectedItem: string;
  confidence: string;
  title: string;
  subtitle: string;
  categorySuggestion: string;
  categoryText: string;
  categoryId: string | null;
  condition: ListingResolvedCondition;
  conditionDescription: string;
  description: string;
  itemSpecifics: ItemSpecific[];
  price: string;
  currency: string;
  quantity: number;
  priceSuggestion: PriceSuggestion;
  shippingNotes: string[];
  searchKeywords: string[];
  buyerQuestions: BuyerQuestion[];
  missingInfoWarnings: string[];
  imageUrls: string[];
  merchantLocationKey: string | null;
  paymentPolicyId: string | null;
  fulfillmentPolicyId: string | null;
  returnPolicyId: string | null;
  publishStatus: PublishStatus;
  sku: string | null;
  offerId: string | null;
  listingId: string | null;
  listingUrl: string | null;
};

export type DraftUpdatePayload = {
  title: string;
  categoryText: string;
  condition: ListingResolvedCondition;
  description: string;
  itemSpecifics: ItemSpecific[];
  price: string;
  quantity: number;
  priceSuggestion: {
    rationale: string;
  };
};
