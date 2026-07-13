import type { TextareaHTMLAttributes } from "react";

interface Props extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean;
}

export function TextArea({ invalid = false, className = "", ...rest }: Props) {
  return (
    <textarea
      className={`w-full rounded-sm border bg-surface px-3 py-2 text-sm text-ink placeholder:text-ink-muted/60
        shadow-[inset_0_1px_2px_rgba(15,20,15,0.05)]
        transition-[border-color,box-shadow] duration-150
        focus:outline-none focus:ring-2 focus:ring-accent-soft focus:border-primary
        ${invalid ? "border-danger" : "border-border-strong"}
        ${className}`}
      {...rest}
    />
  );
}
