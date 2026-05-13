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

export type ListingDraft = {
  draftId: string;
  detectedItem: string;
  confidence: string;
  title: string;
  subtitle: string;
  categorySuggestion: string;
  condition: ListingResolvedCondition;
  conditionDescription: string;
  description: string;
  itemSpecifics: ItemSpecific[];
  priceSuggestion: PriceSuggestion;
  shippingNotes: string[];
  searchKeywords: string[];
  buyerQuestions: BuyerQuestion[];
  missingInfoWarnings: string[];
};

export type DraftUpdatePayload = {
  title: string;
  categorySuggestion: string;
  condition: ListingResolvedCondition;
  description: string;
  itemSpecifics: ItemSpecific[];
  priceSuggestion: {
    amount: string;
    rationale: string;
  };
};
