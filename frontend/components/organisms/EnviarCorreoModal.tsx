"use client";

import { useState } from "react";

import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { FormField } from "../molecules/FormField";
import { Alert } from "../molecules/Alert";
import { Modal } from "../molecules/Modal";
import { ApiError } from "../../lib/api/http";

const REGEX_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

interface Props {
  empresaNombre: string;
  onClose: () => void;
  onEnviar: (destinatario: string) => Promise<{ mensaje: string; modo: "brevo" | "consola" }>;
}

export function EnviarCorreoModal({ empresaNombre, onClose, onEnviar }: Props) {
  const [destinatario, setDestinatario] = useState("");
  const [error, setError] = useState<string | undefined>(undefined);
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [confirmacion, setConfirmacion] = useState<{ mensaje: string; modo: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorGeneral(null);

    if (!destinatario.trim()) {
      setError("El correo del destinatario es obligatorio.");
      return;
    }
    if (!REGEX_CORREO.test(destinatario.trim())) {
      setError("Ingresa un correo válido.");
      return;
    }
    setError(undefined);

    setIsLoading(true);
    try {
      const respuesta = await onEnviar(destinatario.trim());
      setConfirmacion(respuesta);
    } catch (err) {
      setErrorGeneral(err instanceof ApiError ? err.message : "Ocurrió un error inesperado.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal title="Enviar inventario por correo" onClose={onClose} widthClassName="max-w-sm">
      {confirmacion ? (
        <div className="space-y-4">
          <Alert tono={confirmacion.modo === "brevo" ? "exito" : "info"}>{confirmacion.mensaje}</Alert>
          {confirmacion.modo === "consola" && (
            <p className="text-xs text-ink-muted">
              No hay una clave de Brevo (BREVO_API_KEY) configurada en este entorno, así que el
              envío se simuló y quedó registrado en el log del servicio. El PDF sí se generó
              correctamente.
            </p>
          )}
          <div className="flex justify-end border-t border-border pt-4">
            <Button tamano="sm" onClick={onClose}>
              Cerrar
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <p className="text-sm text-ink-muted">
            Se enviará el PDF de inventario de <strong className="text-ink">{empresaNombre}</strong> al
            correo indicado.
          </p>

          {errorGeneral && <Alert tono="peligro">{errorGeneral}</Alert>}

          <FormField htmlFor="destinatario" label="Correo destinatario" required error={error}>
            <Input
              id="destinatario"
              type="email"
              value={destinatario}
              onChange={(event) => setDestinatario(event.target.value)}
              invalid={Boolean(error)}
              placeholder="cliente@empresa.com"
            />
          </FormField>

          <div className="mt-2 flex justify-end gap-2 border-t border-border pt-4">
            <Button type="button" variante="secundario" tamano="sm" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" tamano="sm" isLoading={isLoading}>
              Enviar
            </Button>
          </div>
        </form>
      )}
    </Modal>
  );
}
