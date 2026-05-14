import { EditableField } from "./EditableField";

type PriceSuggestionCardProps = {
  price: string;
  quantity: number;
  confidence: string;
  currency: string;
  rationale: string;
  onPriceChange: (value: string) => void;
  onQuantityChange: (value: number) => void;
  onRationaleChange: (value: string) => void;
};

export function PriceSuggestionCard({
  price,
  quantity,
  confidence,
  currency,
  rationale,
  onPriceChange,
  onQuantityChange,
  onRationaleChange,
}: PriceSuggestionCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        Pricing
      </p>
      <p className="mt-2 text-sm text-muted">
        Currency: {currency} | Confidence: {confidence}
      </p>
      <div className="mt-5 space-y-4">
        <EditableField label="Listing price">
          <input
            type="text"
            value={price}
            className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
            onChange={(event) => onPriceChange(event.target.value)}
          />
        </EditableField>
        <EditableField label="Quantity">
          <input
            type="number"
            min={1}
            step={1}
            value={quantity}
            className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
            onChange={(event) => onQuantityChange(Number(event.target.value) || 1)}
          />
        </EditableField>
        <EditableField label="Pricing rationale">
          <textarea
            rows={4}
            value={rationale}
            className="w-full rounded-2xl border border-border bg-background/50 px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
            onChange={(event) => onRationaleChange(event.target.value)}
          />
        </EditableField>
      </div>
    </section>
  );
}
