"use client";

import { useState } from "react";

import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { Select } from "../atoms/Select";
import { TextArea } from "../atoms/TextArea";
import { FormField } from "../molecules/FormField";
import { Alert } from "../molecules/Alert";
import { Modal } from "../molecules/Modal";
import { PrecioRow } from "../molecules/PrecioRow";
import { ApiError } from "../../lib/api/http";
import type { Empresa } from "../../lib/types/empresa";
import type { Precio, Producto, ProductoInput } from "../../lib/types/producto";

// Alineados con los límites reales del backend: `Producto.codigo` y
// `Producto.nombre` son `CharField` de Django (max_length=50 y 200
// respectivamente, ver backend-django/apps/productos/models.py), y el
// valor de cada precio es un `DecimalField(max_digits=14, decimal_places=2)`
// (backend-django/apps/productos/models.py, PrecioProducto), cuyo entero
// más grande representable es 12 dígitos.
// `caracteristicas` es un `TextField` sin tope técnico en la base de
// datos, pero al ser también la fuente del embedding semántico (ver
// EmbeddingProductoService), un texto libre "ilimitado" no es buena
// práctica: 800 caracteres es un tope de negocio/UX razonable, no una
// restricción del backend.
const CODIGO_MAX_LENGTH = 50;
const NOMBRE_MAX_LENGTH = 200;
const CARACTERISTICAS_MAX_LENGTH = 800;
const PRECIO_VALOR_MAXIMO = 999999999999.99;

interface Errores {
  codigo?: string;
  nombre?: string;
  empresa?: string;
  caracteristicas?: string;
  precios?: string;
}

function validar(data: ProductoInput): Errores {
  const errores: Errores = {};

  if (!data.codigo.trim()) errores.codigo = "El código es obligatorio.";
  else if (data.codigo.trim().length > CODIGO_MAX_LENGTH)
    errores.codigo = `El código no puede superar ${CODIGO_MAX_LENGTH} caracteres.`;

  if (!data.nombre.trim()) errores.nombre = "El nombre es obligatorio.";
  else if (data.nombre.trim().length > NOMBRE_MAX_LENGTH)
    errores.nombre = `El nombre no puede superar ${NOMBRE_MAX_LENGTH} caracteres.`;

  if (!data.empresa) errores.empresa = "Selecciona una empresa.";

  if (data.caracteristicas.length > CARACTERISTICAS_MAX_LENGTH)
    errores.caracteristicas = `Las características no pueden superar ${CARACTERISTICAS_MAX_LENGTH} caracteres.`;

  if (data.precios.length === 0) {
    errores.precios = "Agrega al menos un precio.";
  } else {
    const monedas = data.precios.map((p) => p.moneda);
    const hayDuplicados = new Set(monedas).size !== monedas.length;
    const hayInvalidos = data.precios.some((p) => !p.valor || p.valor <= 0 || Number.isNaN(p.valor));
    const hayExcesivos = data.precios.some((p) => p.valor > PRECIO_VALOR_MAXIMO);
    if (hayDuplicados) errores.precios = "No repitas la misma moneda en más de un precio.";
    else if (hayInvalidos) errores.precios = "Cada precio debe ser mayor a 0.";
    else if (hayExcesivos) errores.precios = `Ningún precio puede superar ${PRECIO_VALOR_MAXIMO.toLocaleString("es-CO")}.`;
  }

  return errores;
}

interface Props {
  productoExistente?: Producto;
  empresas: Empresa[];
  empresaPreseleccionada?: string;
  onClose: () => void;
  onSubmit: (data: ProductoInput) => Promise<void>;
}

export function ProductoFormModal({
  productoExistente,
  empresas,
  empresaPreseleccionada,
  onClose,
  onSubmit,
}: Props) {
  const esEdicion = Boolean(productoExistente);

  const [data, setData] = useState<ProductoInput>({
    codigo: productoExistente?.codigo ?? "",
    nombre: productoExistente?.nombre ?? "",
    caracteristicas: productoExistente?.caracteristicas ?? "",
    empresa: productoExistente?.empresa ?? empresaPreseleccionada ?? empresas[0]?.nit ?? "",
    precios: productoExistente?.precios ?? [{ moneda: "COP", valor: NaN }],
  });
  const [errores, setErrores] = useState<Errores>({});
  const [errorGeneral, setErrorGeneral] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const actualizarPrecio = (index: number, precio: Precio) => {
    setData((prev) => ({
      ...prev,
      precios: prev.precios.map((p, i) => (i === index ? precio : p)),
    }));
  };

  const quitarPrecio = (index: number) => {
    setData((prev) => ({ ...prev, precios: prev.precios.filter((_, i) => i !== index) }));
  };

  const agregarPrecio = () => {
    setData((prev) => ({ ...prev, precios: [...prev.precios, { moneda: "COP", valor: NaN }] }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setErrorGeneral(null);

    const erroresValidacion = validar(data);
    setErrores(erroresValidacion);
    if (Object.keys(erroresValidacion).length > 0) return;

    setIsLoading(true);
    try {
      await onSubmit(data);
    } catch (error) {
      if (error instanceof ApiError) {
        setErrorGeneral(error.message);
      } else {
        setErrorGeneral("Ocurrió un error inesperado. Intenta de nuevo.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal title={esEdicion ? "Editar producto" : "Nuevo producto"} widthClassName="max-w-xl" onClose={onClose}>
      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {errorGeneral && <Alert tono="peligro">{errorGeneral}</Alert>}

        <div className="grid grid-cols-2 gap-4">
          <FormField htmlFor="codigo" label="Código" required error={errores.codigo}>
            <Input
              id="codigo"
              mono
              maxLength={CODIGO_MAX_LENGTH}
              disabled={esEdicion}
              value={data.codigo}
              onChange={(event) => setData({ ...data, codigo: event.target.value })}
              invalid={Boolean(errores.codigo)}
            />
          </FormField>

          <FormField htmlFor="empresa" label="Empresa" required error={errores.empresa}>
            <Select
              id="empresa"
              value={data.empresa}
              onChange={(event) => setData({ ...data, empresa: event.target.value })}
              invalid={Boolean(errores.empresa)}
            >
              {empresas.map((empresa) => (
                <option key={empresa.nit} value={empresa.nit}>
                  {empresa.nombre}
                </option>
              ))}
            </Select>
          </FormField>
        </div>

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
          htmlFor="caracteristicas"
          label="Características"
          error={errores.caracteristicas}
          hint={`${data.caracteristicas.length}/${CARACTERISTICAS_MAX_LENGTH} caracteres`}
        >
          <TextArea
            id="caracteristicas"
            rows={3}
            maxLength={CARACTERISTICAS_MAX_LENGTH}
            value={data.caracteristicas}
            onChange={(event) => setData({ ...data, caracteristicas: event.target.value })}
            invalid={Boolean(errores.caracteristicas)}
          />
        </FormField>

        <FormField htmlFor="precios" label="Precios" required error={errores.precios}>
          <div
            id="precios"
            className="space-y-2 rounded-md border border-border bg-surface-sunken p-3"
          >
            {data.precios.map((precio, index) => (
              <PrecioRow
                key={index}
                precio={precio}
                index={index}
                puedeQuitar={data.precios.length > 1}
                max={PRECIO_VALOR_MAXIMO}
                onChange={actualizarPrecio}
                onQuitar={quitarPrecio}
              />
            ))}
            <Button type="button" variante="texto" tamano="sm" onClick={agregarPrecio}>
              + Agregar moneda
            </Button>
          </div>
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
