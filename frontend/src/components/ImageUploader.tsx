type ImageUploaderProps = {
  disabled?: boolean;
  errorMessage?: string | null;
  isProcessing?: boolean;
  maxImages: number;
  selectedCount: number;
  onSelectFiles: (files: FileList | null) => void;
};

export function ImageUploader({
  disabled = false,
  errorMessage,
  isProcessing = false,
  maxImages,
  selectedCount,
  onSelectFiles,
}: ImageUploaderProps) {
  const remainingSlots = Math.max(maxImages - selectedCount, 0);

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6 shadow-glow backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-2">
          <p className="text-sm uppercase tracking-[0.25em] text-muted">
            Product Photos
          </p>
          <h2 className="text-2xl font-semibold text-text">
            Add up to {maxImages} images
          </h2>
          <p className="max-w-2xl text-sm leading-6 text-muted">
            Use your camera roll or file picker. JPG, PNG, WEBP, and HEIC
            uploads that the browser exposes as images are accepted.
          </p>
        </div>
        <div className="rounded-2xl border border-border bg-surfaceAlt/80 px-4 py-3 text-sm text-muted">
          {selectedCount} selected
          {" | "}
          {remainingSlots} remaining
        </div>
      </div>

      <label className="mt-6 block cursor-pointer rounded-[1.5rem] border border-dashed border-border bg-surfaceAlt/60 p-6 transition hover:border-sky-300/50 hover:bg-surfaceAlt">
        <input
          type="file"
          accept="image/*"
          multiple
          disabled={disabled}
          className="sr-only"
          onChange={(event) => {
            onSelectFiles(event.target.files);
            event.target.value = "";
          }}
        />
        <div className="space-y-3">
          <div className="inline-flex rounded-full border border-sky-400/25 bg-sky-400/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-accent">
            Image upload
          </div>
          <p className="text-lg font-medium text-text">
            {isProcessing
              ? "Preparing previews..."
              : "Tap to choose photos from your device"}
          </p>
          <p className="text-sm leading-6 text-muted">
            The same file input works for desktop uploads and mobile photo
            library selection.
          </p>
        </div>
      </label>

      {errorMessage ? (
        <p className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {errorMessage}
        </p>
      ) : null}
    </section>
  );
}
