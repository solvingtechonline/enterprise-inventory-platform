import type { LoginResponse } from "../types/auth";
import { djangoRequest } from "./http";

/**
 * POST /api/auth/login/
 * Body: {"correo": "...", "password": "..."}
 * El backend valida credenciales y solo el rol Administrador se autentica.
 */
export function login(correo: string, password: string): Promise<LoginResponse> {
  return djangoRequest<LoginResponse>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ correo, password }),
  });
}
