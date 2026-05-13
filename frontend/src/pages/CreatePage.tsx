import { useEffect, useRef, useState } from "react";
import { generateListingDraft } from "../api/listings";
import { ApiError } from "../api/client";
import { ImagePreviewGrid } from "../components/ImagePreviewGrid";
import { ImageUploader } from "../components/ImageUploader";
import { ListingInputForm } from "../components/ListingInputForm";
import type {
  ListingFormValues,
  UploadedImage,
} from "../types/listing";

type CreatePageProps = {
  onNavigateHome: () => void;
};

const MAX_IMAGES = 3;

const initialFormValues: ListingFormValues = {
  condition: "",
  knownIssues: "",
  includedAccessories: "",
  desiredPrice: "",
  sellerNotes: "",
};

const loadingSteps = [
  "Analyzing product photos",
  "Drafting eBay listing",
  "Checking required fields",
];

function createImageId(file: File): string {
  return `${file.name}-${file.size}-${file.lastModified}-${crypto.randomUUID()}`;
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      if (typeof reader.result === "string") {
        resolve(reader.result);
        return;
      }

      reject(new Error("Unable to read image preview data."));
    };

    reader.onerror = () => {
      reject(reader.error ?? new Error("Unable to read image preview data."));
    };

    reader.readAsDataURL(file);
  });
}

export function CreatePage({ onNavigateHome }: CreatePageProps) {
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [formValues, setFormValues] =
    useState<ListingFormValues>(initialFormValues);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const imagesRef = useRef<UploadedImage[]>([]);

  useEffect(() => {
    imagesRef.current = images;
  }, [images]);

  useEffect(() => {
    return () => {
      imagesRef.current.forEach((image) => {
        URL.revokeObjectURL(image.previewUrl);
      });
    };
  }, []);

  useEffect(() => {
    if (!isSubmitting) {
      setLoadingStepIndex(0);
      return;
    }

    const intervalId = window.setInterval(() => {
      setLoadingStepIndex((currentIndex) =>
        currentIndex === loadingSteps.length - 1 ? 0 : currentIndex + 1,
      );
    }, 1200);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [isSubmitting]);

  const handleSelectFiles = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) {
      setErrorMessage("Select at least one image to start a listing draft.");
      return;
    }

    const selectedFiles = Array.from(fileList);
    const nextCount = images.length + selectedFiles.length;

    if (nextCount > MAX_IMAGES) {
      setErrorMessage(
        `You can upload up to ${MAX_IMAGES} images. Remove one before adding more.`,
      );
      return;
    }

    const invalidFile = selectedFiles.find(
      (file) => !file.type || !file.type.startsWith("image/"),
    );

    if (invalidFile) {
      setErrorMessage(
        `"${invalidFile.name}" is not recognized as an image by the browser.`,
      );
      return;
    }

    setErrorMessage(null);

    const nextImages = selectedFiles.map((file) => ({
      id: createImageId(file),
      file,
      previewUrl: URL.createObjectURL(file),
    }));

    setImages((currentImages) => [...currentImages, ...nextImages]);
  };

  const handleRemoveImage = (imageId: string) => {
    setImages((currentImages) => {
      const imageToRemove = currentImages.find((image) => image.id === imageId);

      if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.previewUrl);
      }

      return currentImages.filter((image) => image.id !== imageId);
    });
  };

  const handleFieldChange = <Key extends keyof ListingFormValues>(
    field: Key,
    value: ListingFormValues[Key],
  ) => {
    setFormValues((currentValues) => ({
      ...currentValues,
      [field]: value,
    }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (images.length === 0) {
      setErrorMessage("Add at least one image before continuing.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      const draft = await generateListingDraft(images, formValues);
      const previewImages = await Promise.all(
        images.map(async (image) => ({
          id: image.id,
          previewUrl: await readFileAsDataUrl(image.file),
          name: image.file.name,
        })),
      );

      window.sessionStorage.setItem(
        `listing-draft:${draft.draftId}`,
        JSON.stringify({
          previewImages,
        }),
      );
      window.history.pushState({}, "", `/review/${draft.draftId}`);
      window.dispatchEvent(new PopStateEvent("popstate"));
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Something went wrong while generating the listing draft.";
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-hero px-4 py-6 text-text">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4 rounded-[1.75rem] border border-white/10 bg-surface/65 px-5 py-5 backdrop-blur sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <div className="space-y-2">
            <button
              type="button"
              className="text-sm uppercase tracking-[0.22em] text-muted transition hover:text-text"
              onClick={onNavigateHome}
            >
              Back to landing page
            </button>
            <h1 className="text-3xl font-semibold text-text sm:text-4xl">
              Create listing draft
            </h1>
            <p className="max-w-2xl text-sm leading-6 text-muted sm:text-base">
              Build the input bundle now: product photos, item condition, and
              any notes that should influence the listing draft.
            </p>
          </div>
          <div className="rounded-2xl border border-sky-400/25 bg-sky-400/10 px-4 py-3 text-sm text-accent">
            Generate AI listing drafts
          </div>
        </div>

        <form className="mt-6 space-y-6" onSubmit={handleSubmit}>
          <ImageUploader
            maxImages={MAX_IMAGES}
            selectedCount={images.length}
            errorMessage={errorMessage}
            isProcessing={isSubmitting}
            onSelectFiles={handleSelectFiles}
          />

          <ImagePreviewGrid images={images} onRemoveImage={handleRemoveImage} />

          <ListingInputForm
            values={formValues}
            onChange={handleFieldChange}
          />

          <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="space-y-2">
                <p className="text-sm uppercase tracking-[0.25em] text-muted">
                  Ready State
                </p>
                <h2 className="text-2xl font-semibold text-text">
                  Review before generation
                </h2>
                <p className="max-w-2xl text-sm leading-6 text-muted">
                  Images are required. All seller-input fields remain optional
                  and are sent with the draft generation request.
                </p>
              </div>
              <button
                type="submit"
                disabled={images.length === 0 || isSubmitting}
                className="rounded-2xl bg-accentStrong px-6 py-3 text-base font-medium text-slate-950 transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? loadingSteps[loadingStepIndex] : "Generate Draft"}
              </button>
            </div>

            {images.length === 0 ? (
              <p className="mt-4 rounded-2xl border border-white/8 bg-surfaceAlt/50 px-4 py-3 text-sm text-muted">
                Add at least one product image to enable draft generation.
              </p>
            ) : null}

          </section>
        </form>
      </div>
    </main>
  );
}
