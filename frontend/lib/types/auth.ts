/**
 * Tipos de autenticación.
 *
 * El rol "externo" no proviene del backend (el Externo no se
 * autentica); es el estado por defecto del cliente cuando no hay una
 * sesión de Administrador activa.
 */

export type Rol = "administrador" | "externo";

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface TokenPayload {
  rol: "administrador";
  correo: string;
  exp: number;
  [key: string]: unknown;
}
