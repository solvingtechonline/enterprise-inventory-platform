"use client";

import { useState } from "react";

import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { FormField } from "../molecules/FormField";
import { Alert } from "../molecules/Alert";
import { Modal } from "../molecules/Modal";
import { ApiError } from "../../lib/api/http";
import type { Empresa, EmpresaInput } from "../../lib/types/empresa";

const REGEX_NIT = /^\d{5,15}(-\d)?$/;
const REGEX_TELEFONO = /^\+?\d{7,15}$/;

// Alineados con los límites reales del backend (Django `CharField`), para
// no inventar topes arbitrarios: `Empresa.nombre` es max_length=200 y
// `Empresa.direccion` es max_length=255 (ver backend-django/apps/empresas/models.py).
// `nit` y `telefono` ya quedan acotados por sus regex (16 caracteres como
// máximo válido en ambos casos), así que no necesitan un tope aparte.
const NIT_MAX_LENGTH = 16;
const TELEFONO_MAX_LENGTH = 16;
const NOMBRE_MAX_LENGTH = 200;
const DIRECCION_MAX_LENGTH = 255;

type Errores = Partial<Record<keyof EmpresaInput, string>>;

function validar(data: EmpresaInput, esEdicion: boolean): Errores {
  const errores: Errores = {};

  if (!esEdicion) {
    if (!data.nit.trim()) errores.nit = "El NIT es obligatorio.";
    else if (!REGEX_NIT.test(data.nit.trim()))
      errores.nit = "El NIT debe tener solo dígitos, con un dígito de verificación opcional (ej. 900123456-7).";
  }

  if (!data.nombre.trim()) errores.nombre = "El nombre es obligatorio.";
  else if (data.nombre.trim().length > NOMBRE_MAX_LENGTH)
    errores.nombre = `El nombre no puede superar ${NOMBRE_MAX_LENGTH} caracteres.`;

  if (!data.direccion.trim()) errores.direccion = "La dirección es obligatoria.";
  else if (data.direccion.trim().length > DIRECCION_MAX_LENGTH)
    errores.direccion = `La dirección no puede superar ${DIRECCION_MAX_LENGTH} caracteres.`;

  if (!data.telefono.trim()) errores.telefono = "El teléfono es obligatorio.";
  else if (!REGEX_TELEFONO.test(data.telefono.trim()))
    errores.telefono = "El teléfono debe tener entre 7 y 15 dígitos, con un '+' opcional al inicio.";

  return errores;
}

interface Props {
  empresaExistente?: Empresa;
  onClose: () => void;
  onSubmit: (data: EmpresaInput) => Promise<void>;
}

export function EmpresaFormModal({ empresaExistente, onClose, onSubmit }: Props) {
  const esEdicion = Boolean(empresaExistente);
  const [data, setData] = useState<EmpresaInput>({
    nit: empresaExistente?.nit ?? "",
    nombre: empresaExistente?.nombre ?? "",
    direccion: empresaExistente?.direccion ?? "",
    telefono: empresaExistente?.telefono ?? "",
  });
  const [errores, setErrores] = useState<Errores>({});
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorGeneral(null);

    const erroresValidacion = validar(data, esEdicion);
    setErrores(erroresValidacion);
    if (Object.keys(erroresValidacion).length > 0) return;

    setIsLoading(true);
    try {
      await onSubmit(data);
    } catch (error) {
      if (error instanceof ApiError) {
        setErrores((prev) => ({ ...prev, ...error.fieldErrors }));
        setErrorGeneral(error.fieldErrors ? null : error.message);
      } else {
        setErrorGeneral("Ocurrió un error inesperado. Intenta de nuevo.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal title={esEdicion ? "Editar empresa" : "Nueva empresa"} onClose={onClose}>
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {errorGeneral && <Alert tono="peligro">{errorGeneral}</Alert>}

        <FormField htmlFor="nit" label="NIT" required error={errores.nit}>
          <Input
            id="nit"
            mono
            maxLength={NIT_MAX_LENGTH}
            value={data.nit}
            disabled={esEdicion}
            onChange={(event) => setData({ ...data, nit: event.target.value })}
            invalid={Boolean(errores.nit)}
            placeholder="900123456-7"
          />
        </FormField>

        <FormField
          htmlFor="nombre"
          label="Nombre"
          required
          error={errores.nombre}
          hint={`${data.nombre.length}/${NOMBRE_MAX_LENGTH} caracteres`}
        >
          <Input
            id="nombre"
            maxLength={NOMBRE_MAX_LENGTH}
            value={data.nombre}
            onChange={(event) => setData({ ...data, nombre: event.target.value })}
            invalid={Boolean(errores.nombre)}
          />
        </FormField>

        <FormField
          htmlFor="direccion"
          label="Dirección"
          required
          error={errores.direccion}
          hint={`${data.direccion.length}/${DIRECCION_MAX_LENGTH} caracteres`}
        >
          <Input
            id="direccion"
            maxLength={DIRECCION_MAX_LENGTH}
            value={data.direccion}
            onChange={(event) => setData({ ...data, direccion: event.target.value })}
            invalid={Boolean(errores.direccion)}
          />
        </FormField>

        <FormField htmlFor="telefono" label="Teléfono" required error={errores.telefono}>
          <Input
            id="telefono"
            mono
            maxLength={TELEFONO_MAX_LENGTH}
            value={data.telefono}
            onChange={(event) => setData({ ...data, telefono: event.target.value })}
            invalid={Boolean(errores.telefono)}
            placeholder="+573001234567"
          />
        </FormField>

        <div className="mt-2 flex justify-end gap-2 border-t border-border pt-4">
          <Button type="button" variante="secundario" tamano="sm" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" tamano="sm" isLoading={isLoading}>
            Guardar
          </Button>
        </div>
      </form>
    </Modal>
  );
}
