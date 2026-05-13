import type { ListingFormValues, ListingCondition } from "../types/listing";

type ListingInputFormProps = {
  disabled?: boolean;
  values: ListingFormValues;
  onChange: <Key extends keyof ListingFormValues>(
    field: Key,
    value: ListingFormValues[Key],
  ) => void;
};

const conditionOptions: ListingCondition[] = [
  "New",
  "Like New",
  "Used",
  "For parts/not working",
];

export function ListingInputForm({
  disabled = false,
  values,
  onChange,
}: ListingInputFormProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        Seller Notes
      </p>
      <h2 className="mt-2 text-2xl font-semibold text-text">
        Add optional listing context
      </h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
        These fields are optional and will be sent alongside the uploaded
        images in later phases.
      </p>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <Field label="Condition">
          <select
            value={values.condition}
            disabled={disabled}
            className="w-full rounded-2xl border border-border bg-surfaceAlt px-4 py-3 text-text outline-none transition focus:border-sky-300/60"
            onChange={(event) =>
              onChange("condition", event.target.value as ListingCondition)
            }
          >
            <option value="">Select a condition</option>
            {conditionOptions.map((condition) => (
              <option key={condition} value={condition}>
                {condition}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Desired price">
          <input
            type="text"
            inputMode="decimal"
            placeholder="e.g. 49.99"
            value={values.desiredPrice}
            disabled={disabled}
            className="w-full rounded-2xl border border-border bg-surfaceAlt px-4 py-3 text-text outline-none transition placeholder:text-muted focus:border-sky-300/60"
            onChange={(event) => onChange("desiredPrice", event.target.value)}
          />
        </Field>

        <Field label="Known issues">
          <input
            type="text"
            placeholder="Scratches, missing case, worn box corner..."
            value={values.knownIssues}
            disabled={disabled}
            className="w-full rounded-2xl border border-border bg-surfaceAlt px-4 py-3 text-text outline-none transition placeholder:text-muted focus:border-sky-300/60"
            onChange={(event) => onChange("knownIssues", event.target.value)}
          />
        </Field>

        <Field label="Included accessories">
          <input
            type="text"
            placeholder="Charger, manuals, cables, inserts..."
            value={values.includedAccessories}
            disabled={disabled}
            className="w-full rounded-2xl border border-border bg-surfaceAlt px-4 py-3 text-text outline-none transition placeholder:text-muted focus:border-sky-300/60"
            onChange={(event) =>
              onChange("includedAccessories", event.target.value)
            }
          />
        </Field>

        <div className="md:col-span-2">
          <Field label="Seller notes">
            <textarea
              rows={5}
              placeholder="Anything the AI should prioritize or avoid assuming about the item."
              value={values.sellerNotes}
              disabled={disabled}
              className="w-full rounded-2xl border border-border bg-surfaceAlt px-4 py-3 text-text outline-none transition placeholder:text-muted focus:border-sky-300/60"
              onChange={(event) => onChange("sellerNotes", event.target.value)}
            />
          </Field>
        </div>
      </div>
    </section>
  );
}

type FieldProps = {
  label: string;
  children: React.ReactNode;
};

function Field({ label, children }: FieldProps) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-medium text-slate-200">{label}</span>
      {children}
    </label>
  );
}
