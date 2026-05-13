type WarningBannerProps = {
  warnings: string[];
};

export function WarningBanner({ warnings }: WarningBannerProps) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <section className="rounded-[1.75rem] border border-amber-300/20 bg-amber-300/10 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-amber-100">
        Missing Info Warnings
      </p>
      <div className="mt-4 space-y-3">
        {warnings.map((warning) => (
          <p
            key={warning}
            className="rounded-2xl border border-amber-200/10 bg-surfaceAlt/60 px-4 py-3 text-sm leading-6 text-amber-50"
          >
            {warning}
          </p>
        ))}
      </div>
    </section>
  );
}
