import type { ReactNode } from "react";

type EditableFieldProps = {
  label: string;
  hint?: string;
  children: ReactNode;
};

export function EditableField({ label, hint, children }: EditableFieldProps) {
  return (
    <label className="block space-y-2 rounded-[1.5rem] border border-white/8 bg-surfaceAlt/70 p-4">
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
        {hint ? <p className="text-sm text-muted">{hint}</p> : null}
      </div>
      {children}
    </label>
  );
}
