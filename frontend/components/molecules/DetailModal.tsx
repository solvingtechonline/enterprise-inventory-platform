"use client";

import { Button } from "../atoms/Button";
import { Modal } from "./Modal";

export interface DetailField {
  label: string;
  /** Puede ser texto plano o un nodo ya formateado (ej. un Badge, una lista de precios). */
  value: React.ReactNode;
}

interface Props {
  title: string;
  fields: DetailField[];
  onClose: () => void;
}

/**
 * Modal de solo lectura para consultar el registro completo de una fila de
 * tabla, sin truncar. Genérico a propósito (title + lista de campos) para
 * que `EmpresaTable`, `ProductoTable` e `InventarioTable` lo reutilicen sin
 * duplicar un modal casi idéntico por entidad, mismo criterio que
 * `ConfirmDialog` (molecule que envuelve `Modal` con contenido específico).
 *
 * Layout de una sola columna (etiqueta encima del valor): es la forma más
 * simple de que se vea bien en cualquier ancho de pantalla sin necesitar
 * breakpoints propios, y `Modal` ya se encarga de que el panel completo sea
 * responsive (ancho fluido con tope en `widthClassName`, scroll vertical si
 * el contenido no cabe).
 */
export function DetailModal({ title, fields, onClose }: Props) {
  return (
    <Modal title={title} onClose={onClose} widthClassName="max-w-lg">
      <dl className="divide-y divide-border">
        {fields.map((field) => (
          <div key={field.label} className="py-3 first:pt-0 last:pb-0">
            <dt className="text-xs font-medium uppercase tracking-wide text-ink-muted">
              {field.label}
            </dt>
            <dd className="mt-1 text-sm break-words whitespace-pre-wrap text-ink">
              {field.value || <span className="text-ink-muted">—</span>}
            </dd>
          </div>
        ))}
      </dl>
      <div className="mt-2 flex justify-end border-t border-border pt-4">
        <Button type="button" variante="secundario" tamano="sm" onClick={onClose}>
          Cerrar
        </Button>
      </div>
    </Modal>
  );
}
