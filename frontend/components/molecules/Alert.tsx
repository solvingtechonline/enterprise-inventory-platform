type Tono = "peligro" | "exito" | "info";

interface Props {
  tono?: Tono;
  children: React.ReactNode;
  onDismiss?: () => void;
}

const clasesPorTono: Record<Tono, string> = {
  peligro: "bg-danger-soft text-danger border-danger/40",
  exito: "bg-success-soft text-success border-success/40",
  info: "bg-primary-soft text-primary border-primary/40",
};

export function Alert({ tono = "info", children, onDismiss }: Props) {
  return (
    <div
      className={`flex items-start justify-between gap-3 rounded-sm border px-4 py-3 text-sm shadow-xs animate-alert-in ${clasesPorTono[tono]}`}
      role={tono === "peligro" ? "alert" : "status"}
    >
      <span>{children}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Cerrar aviso"
          className="shrink-0 rounded-sm text-current opacity-70 transition-opacity hover:opacity-100
            focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          ✕
        </button>
      )}
    </div>
  );
}
