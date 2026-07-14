"use client";

import { useCallback, useEffect, useState } from "react";

import { Button } from "../../components/atoms/Button";
import { Badge } from "../../components/atoms/Badge";
import { Spinner } from "../../components/atoms/Spinner";
import { Alert } from "../../components/molecules/Alert";
import { ConfirmDialog } from "../../components/molecules/ConfirmDialog";
import { DetailModal } from "../../components/molecules/DetailModal";
import { EmptyState } from "../../components/molecules/EmptyState";
import { EmpresaFormModal } from "../../components/organisms/EmpresaFormModal";
import { EmpresaTable } from "../../components/organisms/EmpresaTable";
import { PageShell } from "../../components/templates/PageShell";
import { useAuth } from "../../lib/auth/AuthContext";
import {
  actualizarEmpresa,
  crearEmpresa,
  eliminarEmpresa,
  listarEmpresas,
} from "../../lib/api/empresas";
import { ApiError } from "../../lib/api/http";
import type { Empresa, EmpresaInput } from "../../lib/types/empresa";

export default function EmpresasPage() {
  const { token, isAdmin } = useAuth();

  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorCarga, setErrorCarga] = useState<string | null>(null);

  const [modalAbierto, setModalAbierto] = useState(false);
  const [empresaEnEdicion, setEmpresaEnEdicion] = useState<Empresa | undefined>(undefined);
  const [empresaAEliminar, setEmpresaAEliminar] = useState<Empresa | null>(null);
  const [empresaEnDetalle, setEmpresaEnDetalle] = useState<Empresa | null>(null);
  const [isEliminando, setIsEliminando] = useState(false);
  const [avisoExito, setAvisoExito] = useState<string | null>(null);

  const cargarEmpresas = useCallback(async () => {
    setIsLoading(true);
    setErrorCarga(null);
    try {
      const datos = await listarEmpresas();
      setEmpresas(datos);
    } catch (error) {
      setAvisoExito(null);
      setErrorCarga(
        error instanceof ApiError ? error.message : "No se pudieron cargar las empresas.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Sincroniza con la API de Empresas al montar la vista (patrón estándar
    // de carga de datos, no un derivado de estado local).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    cargarEmpresas();
  }, [cargarEmpresas]);

  const abrirCreacion = () => {
    setEmpresaEnEdicion(undefined);
    setModalAbierto(true);
  };

  const abrirEdicion = (empresa: Empresa) => {
    setEmpresaEnEdicion(empresa);
    setModalAbierto(true);
  };

  const handleSubmit = async (data: EmpresaInput) => {
    if (!token) return;
    if (empresaEnEdicion) {
      await actualizarEmpresa(
        empresaEnEdicion.nit,
        { nombre: data.nombre, direccion: data.direccion, telefono: data.telefono },
        token,
      );
      setAvisoExito("Empresa actualizada correctamente.");
    } else {
      await crearEmpresa(data, token);
      setAvisoExito("Empresa creada correctamente.");
    }
    setModalAbierto(false);
    await cargarEmpresas();
  };

  const confirmarEliminacion = async () => {
    if (!empresaAEliminar || !token) return;
    setIsEliminando(true);
    try {
      await eliminarEmpresa(empresaAEliminar.nit, token);
      setEmpresaAEliminar(null);
      setAvisoExito("Empresa eliminada correctamente.");
      await cargarEmpresas();
    } catch (error) {
      setEmpresaAEliminar(null);
      setAvisoExito(null);
      setErrorCarga(error instanceof ApiError ? error.message : "No se pudo eliminar la empresa.");
    } finally {
      setIsEliminando(false);
    }
  };

  return (
    <PageShell
      title="Empresas"
      description="Consulta las empresas registradas. Solo un Administrador puede crear, editar o eliminar."
      actions={
        isAdmin ? (
          <Button tamano="sm" onClick={abrirCreacion}>
            Nueva empresa
          </Button>
        ) : undefined
      }
    >
      {errorCarga && (
        <div className="mb-4">
          <Alert tono="peligro" onDismiss={() => setErrorCarga(null)}>
            {errorCarga}
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

      {isLoading ? (
        <Spinner label="Cargando empresas…" />
      ) : empresas.length === 0 ? (
        <EmptyState
          title="Todavía no hay empresas registradas"
          description={
            isAdmin
              ? "Crea la primera empresa para empezar a asociarle productos e inventario."
              : "Cuando un Administrador registre una empresa, aparecerá aquí."
          }
          action={
            isAdmin ? (
              <Button tamano="sm" onClick={abrirCreacion}>
                Nueva empresa
              </Button>
            ) : undefined
          }
        />
      ) : (
        <EmpresaTable
          empresas={empresas}
          puedeEditar={isAdmin}
          onVerDetalle={setEmpresaEnDetalle}
          onEditar={abrirEdicion}
          onEliminar={setEmpresaAEliminar}
        />
      )}

      {modalAbierto && (
        <EmpresaFormModal
          empresaExistente={empresaEnEdicion}
          onClose={() => setModalAbierto(false)}
          onSubmit={handleSubmit}
        />
      )}

      {empresaAEliminar && (
        <ConfirmDialog
          title="Eliminar empresa"
          description={`¿Eliminar "${empresaAEliminar.nombre}" (${empresaAEliminar.nit})? Esta acción no se puede deshacer. Se eliminarán también sus productos asociados, siempre que ninguno tenga unidades registradas en inventario.`}
          isLoading={isEliminando}
          onConfirm={confirmarEliminacion}
          onCancel={() => setEmpresaAEliminar(null)}
        />
      )}

      {empresaEnDetalle && (
        <DetailModal
          title={`Empresa: ${empresaEnDetalle.nombre}`}
          onClose={() => setEmpresaEnDetalle(null)}
          fields={[
            { label: "NIT", value: <Badge tono="neutro">{empresaEnDetalle.nit}</Badge> },
            { label: "Nombre", value: empresaEnDetalle.nombre },
            { label: "Dirección", value: empresaEnDetalle.direccion },
            { label: "Teléfono", value: empresaEnDetalle.telefono },
          ]}
        />
      )}
    </PageShell>
  );
}
