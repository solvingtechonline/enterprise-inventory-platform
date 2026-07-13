import type { CSSProperties, SelectHTMLAttributes } from "react";

interface Props extends SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean;
}

const flechaSvg =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23666d69' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E\")";

const flechaEstilo: CSSProperties = {
  backgroundImage: flechaSvg,
  backgroundRepeat: "no-repeat",
  backgroundPosition: "right 0.65rem center",
  backgroundSize: "16px",
};

export function Select({ invalid = false, className = "", style, children, ...rest }: Props) {
  return (
    <select
      className={`w-full appearance-none rounded-sm border bg-surface px-3 py-2 pr-9 text-sm text-ink
        shadow-[inset_0_1px_2px_rgba(15,20,15,0.05)]
        transition-[border-color,box-shadow] duration-150
        focus:outline-none focus:ring-2 focus:ring-accent-soft focus:border-primary
        disabled:bg-surface-muted disabled:text-ink-muted
        ${invalid ? "border-danger" : "border-border-strong"}
        ${className}`}
      style={{ ...flechaEstilo, ...style }}
      {...rest}
    >
      {children}
    </select>
  );
}
