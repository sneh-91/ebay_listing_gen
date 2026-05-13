import { apiRequest } from "./client";
import type {
  DraftUpdatePayload,
  ListingDraft,
  ListingFormValues,
  UploadedImage,
} from "../types/listing";

export async function generateListingDraft(
  images: UploadedImage[],
  formValues: ListingFormValues,
): Promise<ListingDraft> {
  const formData = new FormData();

  images.forEach((image) => {
    formData.append("images", image.file);
  });

  if (formValues.condition) {
    formData.append("condition", formValues.condition);
  }

  if (formValues.knownIssues.trim()) {
    formData.append("knownIssues", formValues.knownIssues.trim());
  }

  if (formValues.includedAccessories.trim()) {
    formData.append(
      "includedAccessories",
      formValues.includedAccessories.trim(),
    );
  }

  if (formValues.desiredPrice.trim()) {
    formData.append("desiredPrice", formValues.desiredPrice.trim());
  }

  if (formValues.sellerNotes.trim()) {
    formData.append("sellerNotes", formValues.sellerNotes.trim());
  }

  return apiRequest<ListingDraft>("/api/generate-listing", {
    method: "POST",
    body: formData,
  });
}

export async function getListingDraft(draftId: string): Promise<ListingDraft> {
  return apiRequest<ListingDraft>(`/api/drafts/${draftId}`);
}

export async function updateListingDraft(
  draftId: string,
  payload: DraftUpdatePayload,
): Promise<ListingDraft> {
  return apiRequest<ListingDraft>(`/api/drafts/${draftId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
