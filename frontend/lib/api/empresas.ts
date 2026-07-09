import type { Empresa, EmpresaInput } from "../types/empresa";
import { djangoRequest } from "./http";

/** Lectura pública (rol Externo, sin autenticación). */
export function listarEmpresas(): Promise<Empresa[]> {
  return djangoRequest<Empresa[]>("/empresas/");
}

export function crearEmpresa(data: EmpresaInput, token: string): Promise<Empresa> {
  return djangoRequest<Empresa>("/empresas/", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function actualizarEmpresa(
  nit: string,
  data: Omit<EmpresaInput, "nit">,
  token: string,
): Promise<Empresa> {
  return djangoRequest<Empresa>(`/empresas/${encodeURIComponent(nit)}/`, {
    method: "PATCH",
    body: JSON.stringify(data),
    token,
  });
}

export function eliminarEmpresa(nit: string, token: string): Promise<void> {
  return djangoRequest<void>(`/empresas/${encodeURIComponent(nit)}/`, {
    method: "DELETE",
    token,
  });
}
