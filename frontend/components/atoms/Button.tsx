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
  "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50 " +
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";

const clasesPorVariante: Record<Variante, string> = {
  primario:
    "bg-primary text-white hover:bg-primary-hover focus-visible:outline-primary",
  secundario:
    "bg-transparent text-primary border border-primary/40 hover:bg-primary-soft focus-visible:outline-primary",
  peligro:
    "bg-danger text-white hover:opacity-90 focus-visible:outline-danger",
  texto:
    "bg-transparent text-ink-muted hover:text-ink underline-offset-4 hover:underline focus-visible:outline-primary",
};

const clasesPorTamano: Record<Tamano, string> = {
  sm: "px-3 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
};

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
      {children}
    </button>
  );
}
