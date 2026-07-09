import type { LabelHTMLAttributes } from "react";

interface Props extends LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

export function Label({ required = false, className = "", children, ...rest }: Props) {
  return (
    <label className={`block text-sm font-medium text-ink ${className}`} {...rest}>
      {children}
      {required && <span className="text-danger"> *</span>}
    </label>
  );
}
