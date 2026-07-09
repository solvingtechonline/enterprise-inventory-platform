import type { TextareaHTMLAttributes } from "react";

interface Props extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean;
}

export function TextArea({ invalid = false, className = "", ...rest }: Props) {
  return (
    <textarea
      className={`w-full rounded-sm border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-muted/60
        focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary
        ${invalid ? "border-danger" : "border-border"}
        ${className}`}
      {...rest}
    />
  );
}
