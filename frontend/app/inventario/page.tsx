"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "../../components/atoms/Button";
import { Select } from "../../components/atoms/Select";
import { Spinner } from "../../components/atoms/Spinner";
import { Alert } from "../../components/molecules/Alert";
import { ConfirmDialog } from "../../components/molecules/ConfirmDialog";
import { EmptyState } from "../../components/molecules/EmptyState";
import { InventarioFormModal } from "../../components/organisms/InventarioFormModal";
import { InventarioTable } from "../../components/organisms/InventarioTable";
import { EnviarCorreoModal } from "../../components/organisms/EnviarCorreoModal";
import { AuthGate } from "../../components/templates/AuthGate";
import { PageShell } from "../../components/templates/PageShell";
import { useAuth } from "../../lib/auth/AuthContext";
import { listarEmpresas } from "../../lib/api/empresas";
import { ApiError } from "../../lib/api/http";
import {
  actualizarCantidadInventario,
  descargarReportePdf,
  eliminarInventario,
  enviarReportePorCorreo,
  listarInventario,
  registrarInventario,
} from "../../lib/api/inventario";
import { listarProductos } from "../../lib/api/productos";
import { descargarBlob } from "../../lib/utils/descargarArchivo";
import type { Empresa } from "../../lib/types/empresa";
import type { InventarioRegistro } from "../../lib/types/inventario";
import type { Producto } from "../../lib/types/producto";

function InventarioContenido() {
  const { token } = useAuth();

  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState<string>("");
  const [productos, setProductos] = useState<Producto[]>([]);
  const [registros, setRegistros] = useState<InventarioRegistro[]>([]);

  const [isLoadingEmpresas, setIsLoadingEmpresas] = useState(true);
  const [isLoadingInventario, setIsLoadingInventario] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [registroEnEdicion, setRegistroEnEdicion] = useState<InventarioRegistro | undefined>(undefined);
  const [registroAEliminar, setRegistroAEliminar] = useState<InventarioRegistro | null>(null);
  const [isEliminando, setIsEliminando] = useState(false);

  const [isDescargandoPdf, setIsDescargandoPdf] = useState(false);
  const [modalCorreoAbierto, setModalCorreoAbierto] = useState(false);
  const [avisoExito, setAvisoExito] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    listarEmpresas()
      .then((datos) => {
        setEmpresas(datos);
        if (datos.length > 0) setEmpresaSeleccionada(datos[0].nit);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "No se pudieron cargar las empresas."))
      .finally(() => setIsLoadingEmpresas(false));
  }, [token]);

  const cargarInventarioYProductos = useCallback(async () => {
    if (!token || !empresaSeleccionada) return;
    setIsLoadingInventario(true);
    setError(null);
    try {
      const [listaProductos, listaInventario] = await Promise.all([
        listarProductos(token, empresaSeleccionada),
        listarInventario(empresaSeleccionada, token),
      ]);
      setProductos(listaProductos);
      setRegistros(listaInventario);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar el inventario.");
    } finally {
      setIsLoadingInventario(false);
    }
  }, [token, empresaSeleccionada]);

  useEffect(() => {
    // Sincroniza con Django (Productos) y FastAPI (Inventario) al montar
    // o al cambiar de empresa (patrón estándar de carga de datos).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarInventarioYProductos();
  }, [cargarInventarioYProductos]);

  const empresaActual = empresas.find((empresa) => empresa.nit === empresaSeleccionada);

  const abrirCreacion = () => {
    setRegistroEnEdicion(undefined);
    setModalAbierto(true);
  };

  const abrirEdicion = (registro: InventarioRegistro) => {
    setRegistroEnEdicion(registro);
    setModalAbierto(true);
  };

  const handleSubmit = async (data: { producto_codigo: string; cantidad: number }) => {
    if (!token) return;
    if (registroEnEdicion) {
      await actualizarCantidadInventario(registroEnEdicion.id, data.cantidad, token);
    } else {
      await registrarInventario(
        { empresa_nit: empresaSeleccionada, producto_codigo: data.producto_codigo, cantidad: data.cantidad },
        token,
      );
    }
    setModalAbierto(false);
    await cargarInventarioYProductos();
  };

  const confirmarEliminacion = async () => {
    if (!registroAEliminar || !token) return;
    setIsEliminando(true);
    try {
      await eliminarInventario(registroAEliminar.id, token);
      setRegistroAEliminar(null);
      await cargarInventarioYProductos();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo eliminar el registro.");
    } finally {
      setIsEliminando(false);
    }
  };

  const handleDescargarPdf = async () => {
    if (!token || !empresaSeleccionada) return;
    setIsDescargandoPdf(true);
    setError(null);
    try {
      const { blob, nombreArchivo } = await descargarReportePdf(empresaSeleccionada, token);
      descargarBlob(blob, nombreArchivo);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo generar el PDF de inventario.");
    } finally {
      setIsDescargandoPdf(false);
    }
  };

  const handleEnviarCorreo = async (destinatario: string) => {
    if (!token || !empresaSeleccionada) {
      throw new Error("No hay una empresa seleccionada.");
    }
    const respuesta = await enviarReportePorCorreo(empresaSeleccionada, destinatario, token);
    setAvisoExito(respuesta.mensaje);
    return respuesta;
  };

  if (isLoadingEmpresas) return <Spinner label="Cargando empresas…" />;

  if (empresas.length === 0) {
    return (
      <EmptyState
        title="Registra una empresa antes de gestionar inventario"
        description="El inventario siempre está asociado a una empresa existente."
      />
    );
  }

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

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="w-64">
          <Select
            aria-label="Seleccionar empresa"
            value={empresaSeleccionada}
            onChange={(event) => setEmpresaSeleccionada(event.target.value)}
          >
            {empresas.map((empresa) => (
              <option key={empresa.nit} value={empresa.nit}>
                {empresa.nombre}
              </option>
            ))}
          </Select>
        </div>
        <Button tamano="sm" onClick={abrirCreacion} disabled={productos.length === 0}>
          Registrar producto
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        <Button
          variante="secundario"
          tamano="sm"
          onClick={handleDescargarPdf}
          isLoading={isDescargandoPdf}
          disabled={registros.length === 0}
        >
          Descargar PDF
        </Button>
        <Button
          variante="secundario"
          tamano="sm"
          onClick={() => setModalCorreoAbierto(true)}
          disabled={registros.length === 0}
        >
          Enviar por correo
        </Button>
      </div>

      {isLoadingInventario ? (
        <Spinner label="Cargando inventario…" />
      ) : productos.length === 0 ? (
        <EmptyState
          title="Esta empresa no tiene productos"
          description="Registra productos para esta empresa antes de gestionar su inventario."
        />
      ) : registros.length === 0 ? (
        <EmptyState
          title="Sin registros de inventario"
          description="Registra el primer producto en el inventario de esta empresa."
          action={
            <Button tamano="sm" onClick={abrirCreacion}>
              Registrar producto
            </Button>
          }
        />
      ) : (
        <InventarioTable
          registros={registros}
          productos={productos}
          onEditar={abrirEdicion}
          onEliminar={setRegistroAEliminar}
        />
      )}

      {modalAbierto && empresaActual && (
        <InventarioFormModal
          empresaNombre={empresaActual.nombre}
          productos={productos}
          registroExistente={registroEnEdicion}
          onClose={() => setModalAbierto(false)}
          onSubmit={handleSubmit}
        />
      )}

      {registroAEliminar && (
        <ConfirmDialog
          title="Eliminar registro de inventario"
          description={`¿Eliminar el registro de "${registroAEliminar.producto_codigo}"? Esta acción no se puede deshacer.`}
          isLoading={isEliminando}
          onConfirm={confirmarEliminacion}
          onCancel={() => setRegistroAEliminar(null)}
        />
      )}

      {modalCorreoAbierto && empresaActual && (
        <EnviarCorreoModal
          empresaNombre={empresaActual.nombre}
          onClose={() => setModalCorreoAbierto(false)}
          onEnviar={handleEnviarCorreo}
        />
      )}
    </>
  );
}

export default function InventarioPage() {
  return (
    <PageShell
      title="Inventario"
      description="Registro y consulta de existencias por empresa. Requiere rol Administrador."
    >
      <AuthGate>
        <InventarioContenido />
      </AuthGate>
    </PageShell>
  );
}
