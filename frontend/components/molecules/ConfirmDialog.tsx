"use client";

import { Button } from "../atoms/Button";
import { Modal } from "./Modal";

interface Props {
  title: string;
  description: string;
  confirmLabel?: string;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel = "Eliminar",
  isLoading = false,
  onConfirm,
  onCancel,
}: Props) {
  return (
    <Modal title={title} onClose={onCancel} widthClassName="max-w-sm">
      <p className="text-sm text-ink-muted">{description}</p>
      <div className="mt-5 flex justify-end gap-2 border-t border-border pt-4">
        <Button variante="secundario" tamano="sm" onClick={onCancel} disabled={isLoading}>
          Cancelar
        </Button>
        <Button variante="peligro" tamano="sm" onClick={onConfirm} isLoading={isLoading}>
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  );
}
