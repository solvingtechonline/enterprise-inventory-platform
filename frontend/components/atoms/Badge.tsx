type Tono = "primario" | "neutro" | "exito" | "peligro";

interface Props {
  tono?: Tono;
  children: React.ReactNode;
  className?: string;
}

const clasesPorTono: Record<Tono, string> = {
  primario: "bg-primary-soft text-primary",
  neutro: "bg-surface-muted text-ink-muted",
  exito: "bg-success-soft text-success",
  peligro: "bg-danger-soft text-danger",
};

export function Badge({ tono = "neutro", children, className = "" }: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold font-mono tracking-wide ${clasesPorTono[tono]} ${className}`}
    >
      {children}
    </span>
  );
}
