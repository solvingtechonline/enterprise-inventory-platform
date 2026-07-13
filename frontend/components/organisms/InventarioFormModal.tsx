"use client";

import { useState } from "react";

import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { Select } from "../atoms/Select";
import { FormField } from "../molecules/FormField";
import { Alert } from "../molecules/Alert";
import { Modal } from "../molecules/Modal";
import { ApiError } from "../../lib/api/http";
import type { InventarioRegistro } from "../../lib/types/inventario";
import type { Producto } from "../../lib/types/producto";

interface Props {
  empresaNombre: string;
  productos: Producto[];
  registroExistente?: InventarioRegistro;
  onClose: () => void;
  onSubmit: (data: { producto_codigo: string; cantidad: number }) => Promise<void>;
}

export function InventarioFormModal({
  empresaNombre,
  productos,
  registroExistente,
  onClose,
  onSubmit,
}: Props) {
  const esEdicion = Boolean(registroExistente);

  const [productoCodigo, setProductoCodigo] = useState(
    registroExistente?.producto_codigo ?? productos[0]?.codigo ?? "",
  );
  const [cantidad, setCantidad] = useState<number>(registroExistente?.cantidad ?? NaN);
  const [errores, setErrores] = useState<{ producto?: string; cantidad?: string }>({});
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorGeneral(null);

    const erroresValidacion: { producto?: string; cantidad?: string } = {};
    if (!esEdicion && !productoCodigo) erroresValidacion.producto = "Selecciona un producto.";
    if (Number.isNaN(cantidad)) erroresValidacion.cantidad = "Ingresa una cantidad.";
    else if (esEdicion && cantidad < 0) erroresValidacion.cantidad = "La cantidad no puede ser negativa.";
    else if (!esEdicion && cantidad <= 0) erroresValidacion.cantidad = "La cantidad debe ser mayor a 0.";
    setErrores(erroresValidacion);
    if (Object.keys(erroresValidacion).length > 0) return;

    setIsLoading(true);
    try {
      await onSubmit({ producto_codigo: productoCodigo, cantidad });
    } catch (error) {
      setErrorGeneral(error instanceof ApiError ? error.message : "Ocurrió un error inesperado.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      title={esEdicion ? "Corregir cantidad" : "Registrar producto en inventario"}
      onClose={onClose}
    >
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {errorGeneral && <Alert tono="peligro">{errorGeneral}</Alert>}

        <FormField htmlFor="empresa" label="Empresa">
          <Input id="empresa" value={empresaNombre} disabled />
        </FormField>

        <FormField htmlFor="producto" label="Producto" required error={errores.producto}>
          {esEdicion ? (
            <Input
              id="producto"
              mono
              value={`${registroExistente?.producto_codigo} - ${
                productos.find((p) => p.codigo === registroExistente?.producto_codigo)?.nombre ?? ""
              }`}
              disabled
            />
          ) : (
            <Select
              id="producto"
              value={productoCodigo}
              onChange={(event) => setProductoCodigo(event.target.value)}
              invalid={Boolean(errores.producto)}
            >
              {productos.map((producto) => (
                <option key={producto.codigo} value={producto.codigo}>
                  {producto.codigo} - {producto.nombre}
                </option>
              ))}
            </Select>
          )}
        </FormField>

        <FormField
          htmlFor="cantidad"
          label="Cantidad"
          required
          error={errores.cantidad}
          hint={
            esEdicion
              ? "Corrige la cantidad absoluta en inventario."
              : "Si el producto ya está registrado, esta cantidad se suma al stock existente."
          }
        >
          <Input
            id="cantidad"
            mono
            type="number"
            min={esEdicion ? 0 : 1}
            value={Number.isNaN(cantidad) ? "" : cantidad}
            onChange={(event) => setCantidad(event.target.valueAsNumber)}
            invalid={Boolean(errores.cantidad)}
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
