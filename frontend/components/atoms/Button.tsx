import type { ButtonHTMLAttributes } from "react";

type Variante = "primario" | "secundario" | "peligro" | "texto";
type Tamano = "sm" | "md";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante;
  tamano?: Tamano;
  isLoading?: boolean;
}

const baseClases =
  "inline-flex items-center justify-center gap-2 rounded-sm font-sans font-medium " +
  "transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:scale-100 " +
  "active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

const clasesPorVariante: Record<Variante, string> = {
  primario:
    "bg-primary text-primary-ink shadow-xs hover:bg-primary-hover hover:shadow-sm hover:-translate-y-px",
  secundario:
    "bg-transparent text-primary border border-border-strong hover:border-primary hover:bg-primary-soft",
  peligro:
    "bg-danger text-danger-ink shadow-xs hover:bg-danger-hover hover:-translate-y-px " +
    "hover:shadow-[0_10px_22px_-8px_rgba(200,50,31,0.55)]",
  texto:
    "bg-transparent text-ink-muted hover:text-ink underline-offset-4 hover:underline",
};

const clasesPorTamano: Record<Tamano, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
};

function IconoPapelera() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-3.5 w-3.5"
      aria-hidden="true"
    >
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6" />
      <path d="M14 11v6" />
    </svg>
  );
}

export function Button({
  variante = "primario",
  tamano = "md",
  isLoading = false,
  className = "",
  disabled,
  children,
  ...rest
}: Props) {
  return (
    <button
      className={`${baseClases} ${clasesPorVariante[variante]} ${clasesPorTamano[tamano]} ${className}`}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading && (
        <span
          className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
          aria-hidden="true"
        />
      )}
      {!isLoading && variante === "peligro" && <IconoPapelera />}
      {children}
    </button>
  );
}
