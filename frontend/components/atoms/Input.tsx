import type { InputHTMLAttributes } from "react";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
  mono?: boolean;
}

export function Input({ invalid = false, mono = false, className = "", ...rest }: Props) {
  return (
    <input
      className={`w-full rounded-sm border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-muted/60
        shadow-[inset_0_1px_2px_rgba(15,20,15,0.05)]
        transition-[border-color,box-shadow] duration-150
        focus:outline-none focus:ring-2 focus:ring-accent-soft focus:border-primary
        disabled:bg-surface-muted disabled:text-ink-muted
        ${mono ? "font-mono" : "font-sans"}
        ${invalid ? "border-danger" : "border-border-strong"}
        ${className}`}
      {...rest}
    />
  );
}
