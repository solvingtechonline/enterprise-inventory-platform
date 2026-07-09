import type { BusquedaSemanticaRead } from "../types/ia";
import { fastapiRequest } from "./http";

/**
 * El agente de IA (búsqueda semántica de productos) vive en FastAPI,
 * igual que Inventario. Requiere rol Administrador (mismo criterio que
 * `backend-fastapi/app/api/ia.py`: `dependencies=[Depends(requerir_administrador)]`).
 */
export function buscarProductosSemantico(
  consulta: string,
  token: string,
  limite = 5,
): Promise<BusquedaSemanticaRead> {
  const query = new URLSearchParams({ consulta, limite: String(limite) });
  return fastapiRequest<BusquedaSemanticaRead>(`/api/ia/buscar?${query.toString()}`, {
    token,
  });
}
