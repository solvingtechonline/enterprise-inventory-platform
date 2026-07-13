"use client";

import { useEffect, useRef } from "react";

interface Props {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  widthClassName?: string;
}

const SELECTOR_FOCUABLE =
  'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function Modal({ title, onClose, children, widthClassName = "max-w-lg" }: Props) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  // Foco inicial al abrir + restaurar el foco al elemento que abrió el
  // modal al cerrarlo (patrón estándar de diálogo accesible).
  useEffect(() => {
    const elementoPrevio = document.activeElement as HTMLElement | null;
    const panel = panelRef.current;
    const primerFocuable = panel?.querySelector<HTMLElement>(SELECTOR_FOCUABLE);
    (primerFocuable ?? panel)?.focus();

    return () => {
      elementoPrevio?.focus();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Focus trap: Tab/Shift+Tab no debe poder salir del modal mientras esté
  // abierto (WCAG 2.1.2 "No Keyboard Trap" se cumple en sentido inverso:
  // el foco debe quedar atrapado adentro, no afuera).
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Tab") return;
      const panel = panelRef.current;
      if (!panel) return;

      const focuables = Array.from(panel.querySelectorAll<HTMLElement>(SELECTOR_FOCUABLE));
      if (focuables.length === 0) {
        event.preventDefault();
        return;
      }

      const primero = focuables[0];
      const ultimo = focuables[focuables.length - 1];

      if (event.shiftKey && document.activeElement === primero) {
        event.preventDefault();
        ultimo.focus();
      } else if (!event.shiftKey && document.activeElement === ultimo) {
        event.preventDefault();
        primero.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-ink/40 px-4 py-10 backdrop-blur-sm animate-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onClick={onClose}
    >
      <div
        ref={panelRef}
        tabIndex={-1}
        className={`w-full ${widthClassName} rounded-lg border border-border bg-surface shadow-lg animate-modal-panel focus:outline-none`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <h2 id="modal-title" className="font-display text-lg font-semibold text-ink">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="rounded-sm p-1 text-ink-muted transition-colors hover:bg-surface-muted hover:text-ink
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            ✕
          </button>
        </div>
        <div className="px-5 py-4">{children}</div>
      </div>
    </div>
  );
}
