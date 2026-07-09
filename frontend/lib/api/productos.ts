import type { Producto, ProductoInput } from "../types/producto";
import { djangoRequest } from "./http";

/**
 * Todas las operaciones sobre Productos requieren rol Administrador,
 * incluida la lectura (ver apps/productos/views.py: supuesto documentado
 * de seguridad por defecto, ya que la especificación solo exime de
 * autenticación la visualización de Empresas).
 */
export function listarProductos(token: string, empresaNit?: string): Promise<Producto[]> {
  const query = empresaNit ? `?empresa=${encodeURIComponent(empresaNit)}` : "";
  return djangoRequest<Producto[]>(`/productos/${query}`, { token });
}

export function crearProducto(data: ProductoInput, token: string): Promise<Producto> {
  return djangoRequest<Producto>("/productos/", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function actualizarProducto(
  id: number,
  data: Omit<ProductoInput, "codigo"> & { codigo: string },
  token: string,
): Promise<Producto> {
  return djangoRequest<Producto>(`/productos/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function eliminarProducto(id: number, token: string): Promise<void> {
  return djangoRequest<void>(`/productos/${id}/`, {
    method: "DELETE",
    token,
  });
}
