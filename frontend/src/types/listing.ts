export type ListingCondition =
  | ""
  | "New"
  | "Like New"
  | "Used"
  | "For parts/not working";

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
