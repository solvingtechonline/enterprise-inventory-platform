import type { InputHTMLAttributes } from "react";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
  mono?: boolean;
}

export function Input({ invalid = false, mono = false, className = "", ...rest }: Props) {
  return (
    <input
      className={`w-full rounded-sm border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-muted/60
        focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
        disabled:bg-surface-muted disabled:text-ink-muted
        ${mono ? "font-mono" : "font-sans"}
        ${invalid ? "border-danger" : "border-border"}
        ${className}`}
      {...rest}
    />
  );
}
