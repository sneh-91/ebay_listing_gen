import type { UploadedImage } from "../types/listing";

type ImagePreviewGridProps = {
  images: UploadedImage[];
  onRemoveImage: (imageId: string) => void;
};

function formatFileSize(sizeInBytes: number): string {
  if (sizeInBytes < 1024 * 1024) {
    return `${(sizeInBytes / 1024).toFixed(0)} KB`;
  }

  return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ImagePreviewGrid({
  images,
  onRemoveImage,
}: ImagePreviewGridProps) {
  if (images.length === 0) {
    return (
      <section className="rounded-[1.75rem] border border-white/10 bg-surface/70 p-6">
        <p className="text-sm uppercase tracking-[0.25em] text-muted">
          Preview Grid
        </p>
        <div className="mt-4 rounded-[1.5rem] border border-dashed border-border bg-surfaceAlt/40 px-5 py-10 text-center">
          <p className="text-lg font-medium text-text">No images added yet</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            Your selected product photos will appear here before submission.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/70 p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-muted">
            Preview Grid
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-text">
            Review selected images
          </h2>
        </div>
        <p className="text-sm text-muted">{images.length} ready</p>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {images.map((image) => (
          <article
            key={image.id}
            className="overflow-hidden rounded-[1.5rem] border border-white/8 bg-surfaceAlt/70"
          >
            <div className="aspect-[4/3] overflow-hidden bg-background">
              <img
                src={image.previewUrl}
                alt={image.file.name}
                className="h-full w-full object-cover"
              />
            </div>
            <div className="space-y-3 p-4">
              <div>
                <p className="truncate text-sm font-medium text-text">
                  {image.file.name}
                </p>
                <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted">
                  {image.file.type || "image"} | {formatFileSize(image.file.size)}
                </p>
              </div>
              <button
                type="button"
                className="rounded-2xl border border-border px-3 py-2 text-sm font-medium text-text transition hover:border-rose-300/60 hover:bg-rose-400/10"
                onClick={() => onRemoveImage(image.id)}
              >
                Remove image
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
