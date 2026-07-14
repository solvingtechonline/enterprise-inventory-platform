"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "../../components/atoms/Button";
import { Badge } from "../../components/atoms/Badge";
import { Select } from "../../components/atoms/Select";
import { Spinner } from "../../components/atoms/Spinner";
import { Alert } from "../../components/molecules/Alert";
import { ConfirmDialog } from "../../components/molecules/ConfirmDialog";
import { DetailModal } from "../../components/molecules/DetailModal";
import { EmptyState } from "../../components/molecules/EmptyState";
import { BusquedaSemanticaProductos } from "../../components/organisms/BusquedaSemanticaProductos";
import { ProductoFormModal } from "../../components/organisms/ProductoFormModal";
import { ProductoTable } from "../../components/organisms/ProductoTable";
import { AuthGate } from "../../components/templates/AuthGate";
import { PageShell } from "../../components/templates/PageShell";
import { useAuth } from "../../lib/auth/AuthContext";
import { listarEmpresas } from "../../lib/api/empresas";
import { ApiError } from "../../lib/api/http";
import {
  actualizarProducto,
  crearProducto,
  eliminarProducto,
  listarProductos,
} from "../../lib/api/productos";
import type { Empresa } from "../../lib/types/empresa";
import type { Producto, ProductoInput } from "../../lib/types/producto";

function ProductosContenido() {
  const { token } = useAuth();

  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [empresaFiltro, setEmpresaFiltro] = useState<string>("");
  const [productos, setProductos] = useState<Producto[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [productoEnEdicion, setProductoEnEdicion] = useState<Producto | undefined>(undefined);
  const [productoAEliminar, setProductoAEliminar] = useState<Producto | null>(null);
  const [productoEnDetalle, setProductoEnDetalle] = useState<Producto | null>(null);
  const [isEliminando, setIsEliminando] = useState(false);
  const [avisoExito, setAvisoExito] = useState<string | null>(null);

  const cargarTodo = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const listaEmpresas = await listarEmpresas();
      setEmpresas(listaEmpresas);
      const listaProductos = await listarProductos(token, empresaFiltro || undefined);
      setProductos(listaProductos);
    } catch (err) {
      setAvisoExito(null);
      setError(err instanceof ApiError ? err.message : "No se pudieron cargar los productos.");
    } finally {
      setIsLoading(false);
    }
  }, [token, empresaFiltro]);

  useEffect(() => {
    // Sincroniza con las APIs de Empresas/Productos al montar o al cambiar
    // el filtro (patrón estándar de carga de datos).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarTodo();
  }, [cargarTodo]);

  const abrirCreacion = () => {
    setProductoEnEdicion(undefined);
    setModalAbierto(true);
  };

  const abrirEdicion = (producto: Producto) => {
    setProductoEnEdicion(producto);
    setModalAbierto(true);
  };

  const handleSubmit = async (data: ProductoInput) => {
    if (!token) return;
    if (productoEnEdicion) {
      await actualizarProducto(productoEnEdicion.id, data, token);
      setAvisoExito("Producto actualizado correctamente.");
    } else {
      await crearProducto(data, token);
      setAvisoExito("Producto creado correctamente.");
    }
    setModalAbierto(false);
    await cargarTodo();
  };

  const confirmarEliminacion = async () => {
    if (!productoAEliminar || !token) return;
    setIsEliminando(true);
    try {
      await eliminarProducto(productoAEliminar.id, token);
      setProductoAEliminar(null);
      setAvisoExito("Producto eliminado correctamente.");
      await cargarTodo();
    } catch (err) {
      setProductoAEliminar(null);
      setAvisoExito(null);
      setError(err instanceof ApiError ? err.message : "No se pudo eliminar el producto.");
    } finally {
      setIsEliminando(false);
    }
  };

  if (isLoading) return <Spinner label="Cargando productos…" />;

  return (
    <>
      {error && (
        <div className="mb-4">
          <Alert tono="peligro" onDismiss={() => setError(null)}>
            {error}
          </Alert>
        </div>
      )}

      {avisoExito && (
        <div className="mb-4">
          <Alert tono="exito" onDismiss={() => setAvisoExito(null)}>
            {avisoExito}
          </Alert>
        </div>
      )}

      {token && (
        <BusquedaSemanticaProductos token={token} onFiltrarEmpresa={setEmpresaFiltro} />
      )}

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="w-64">
          <Select
            aria-label="Filtrar por empresa"
            value={empresaFiltro}
            onChange={(event) => setEmpresaFiltro(event.target.value)}
          >
            <option value="">Todas las empresas</option>
            {empresas.map((empresa) => (
              <option key={empresa.nit} value={empresa.nit}>
                {empresa.nombre}
              </option>
            ))}
          </Select>
        </div>
        <Button tamano="sm" onClick={abrirCreacion} disabled={empresas.length === 0}>
          Nuevo producto
        </Button>
      </div>

      {empresas.length === 0 ? (
        <EmptyState
          title="Registra una empresa antes de crear productos"
          description="Un producto siempre pertenece a una empresa existente."
        />
      ) : productos.length === 0 ? (
        <EmptyState
          title="No hay productos para este filtro"
          description="Crea un producto o cambia la empresa seleccionada."
          action={
            <Button tamano="sm" onClick={abrirCreacion}>
              Nuevo producto
            </Button>
          }
        />
      ) : (
        <ProductoTable
          productos={productos}
          empresas={empresas}
          onVerDetalle={setProductoEnDetalle}
          onEditar={abrirEdicion}
          onEliminar={setProductoAEliminar}
        />
      )}

      {modalAbierto && (
        <ProductoFormModal
          productoExistente={productoEnEdicion}
          empresas={empresas}
          empresaPreseleccionada={empresaFiltro || undefined}
          onClose={() => setModalAbierto(false)}
          onSubmit={handleSubmit}
        />
      )}

      {productoAEliminar && (
        <ConfirmDialog
          title="Eliminar producto"
          description={`¿Eliminar "${productoAEliminar.nombre}" (${productoAEliminar.codigo})? Esta acción no se puede deshacer.`}
          isLoading={isEliminando}
          onConfirm={confirmarEliminacion}
          onCancel={() => setProductoAEliminar(null)}
        />
      )}

      {productoEnDetalle && (
        <DetailModal
          title={`Producto: ${productoEnDetalle.nombre}`}
          onClose={() => setProductoEnDetalle(null)}
          fields={[
            { label: "Código", value: <Badge tono="neutro">{productoEnDetalle.codigo}</Badge> },
            { label: "Nombre", value: productoEnDetalle.nombre },
            {
              label: "Empresa",
              value:
                empresas.find((empresa) => empresa.nit === productoEnDetalle.empresa)?.nombre ??
                productoEnDetalle.empresa,
            },
            { label: "Características", value: productoEnDetalle.caracteristicas || undefined },
            {
              label: "Precios",
              value: (
                <div className="flex flex-wrap gap-2">
                  {productoEnDetalle.precios.map((precio) => (
                    <span key={precio.moneda} className="font-mono text-sm">
                      {precio.moneda} {precio.valor.toLocaleString("es-CO", { minimumFractionDigits: 2 })}
                    </span>
                  ))}
                </div>
              ),
            },
          ]}
        />
      )}
    </>
  );
}

export default function ProductosPage() {
  return (
    <PageShell
      title="Productos"
      description="Gestión de productos asociados a una empresa. Requiere rol Administrador."
    >
      <AuthGate>
        <ProductosContenido />
      </AuthGate>
    </PageShell>
  );
}
