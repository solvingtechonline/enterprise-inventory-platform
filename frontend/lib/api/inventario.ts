import type { InventarioRegistrarInput, InventarioRegistro } from "../types/inventario";
import { fastapiBlobRequest, fastapiRequest } from "./http";

/**
 * FastAPI es dueño exclusivo de la tabla Inventario.
 * Todas las operaciones requieren el token de Django con rol
 * Administrador; FastAPI no emite ni gestiona sesiones.
 */
export function listarInventario(empresaNit: string, token: string): Promise<InventarioRegistro[]> {
  return fastapiRequest<InventarioRegistro[]>(
    `/api/inventario/?empresa_nit=${encodeURIComponent(empresaNit)}`,
    { token },
  );
}

export function registrarInventario(
  data: InventarioRegistrarInput,
  token: string,
): Promise<InventarioRegistro> {
  return fastapiRequest<InventarioRegistro>("/api/inventario/", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function actualizarCantidadInventario(
  id: number,
  cantidad: number,
  token: string,
): Promise<InventarioRegistro> {
  return fastapiRequest<InventarioRegistro>(`/api/inventario/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ cantidad }),
    token,
  });
}

export function eliminarInventario(id: number, token: string): Promise<void> {
  return fastapiRequest<void>(`/api/inventario/${id}`, {
    method: "DELETE",
    token,
  });
}

/** Descarga el PDF de inventario de una empresa (Blob listo para guardar en el navegador). */
export async function descargarReportePdf(
  empresaNit: string,
  token: string,
): Promise<{ blob: Blob; nombreArchivo: string }> {
  const blob = await fastapiBlobRequest(
    `/api/inventario/reporte/pdf?empresa_nit=${encodeURIComponent(empresaNit)}`,
    { token },
  );
  return { blob, nombreArchivo: `inventario_${empresaNit}.pdf` };
}

export interface ReporteEnviarRespuesta {
  mensaje: string;
  modo: "brevo" | "consola";
}

/** Genera el PDF de inventario de una empresa y lo envía por correo al destinatario indicado. */
export function enviarReportePorCorreo(
  empresaNit: string,
  destinatario: string,
  token: string,
): Promise<ReporteEnviarRespuesta> {
  return fastapiRequest<ReporteEnviarRespuesta>("/api/inventario/reporte/enviar", {
    method: "POST",
    body: JSON.stringify({ empresa_nit: empresaNit, destinatario }),
    token,
  });
}
