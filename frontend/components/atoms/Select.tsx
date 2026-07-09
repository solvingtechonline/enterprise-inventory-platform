import type { SelectHTMLAttributes } from "react";

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean;
}

export function Select({ invalid = false, className = "", children, ...rest }: Props) {
  return (
    <select
      className={`w-full rounded-sm border bg-surface px-3 py-2 text-sm text-ink
        focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
        disabled:bg-surface-muted disabled:text-ink-muted
        ${invalid ? "border-danger" : "border-border"}
        ${className}`}
      {...rest}
    >
      {children}
    </select>
  );
}
