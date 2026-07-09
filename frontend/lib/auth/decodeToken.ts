import type { TokenPayload } from "../types/auth";

/**
 * Decodifica (sin verificar) el payload de un JWT para leer los claims
 * `rol`, `correo` y `exp` emitidos por Django. No sustituye la validación
 * de firma, que siempre ocurre en el backend (Django/FastAPI); aquí solo
 * sirve para que la interfaz sepa qué mostrar y cuándo expiró la sesión.
 */
export function decodeTokenPayload(token: string): TokenPayload | null {
  try {
    const [, payloadBase64] = token.split(".");
    if (!payloadBase64) return null;

    const normalizado = payloadBase64.replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(normalizado);
    return JSON.parse(json) as TokenPayload;
  } catch {
    return null;
  }
}

export function tokenEstaVencido(payload: TokenPayload): boolean {
  const ahoraEnSegundos = Date.now() / 1000;
  return payload.exp <= ahoraEnSegundos;
}
