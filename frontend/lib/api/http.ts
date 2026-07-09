/**
 * Cliente HTTP compartido por Django (Empresas/Productos/Login) y FastAPI
 * (Inventario). Ambos backends son consumidos vía REST desde el frontend
 * (Next.js no asume responsabilidades de backend); este módulo solo
 * centraliza fetch, headers y parseo de errores.
 */

import { DJANGO_API_URL, FASTAPI_API_URL } from "./config";

/** Error homogéneo para toda la app, con errores de campo cuando el backend los expone. */
export class ApiError extends Error {
  readonly status: number;
  readonly fieldErrors?: Record<string, string[]>;

  constructor(message: string, status: number, fieldErrors?: Record<string, string[]>) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.fieldErrors = fieldErrors;
  }
}

interface RequestOptions extends Omit<RequestInit, "headers"> {
  token?: string | null;
  headers?: Record<string, string>;
}

function parseJsonSafe(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function buildApiError(status: number, data: unknown): ApiError {
  if (status === 401) {
    return new ApiError("Tu sesión no es válida o expiró. Inicia sesión de nuevo.", status);
  }

  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;

    if (typeof record.detail === "string") {
      return new ApiError(record.detail, status);
    }

    // Errores de validación estilo DRF: { campo: ["mensaje", ...] }
    const fieldErrors: Record<string, string[]> = {};
    for (const [campo, valor] of Object.entries(record)) {
      fieldErrors[campo] = Array.isArray(valor) ? valor.map(String) : [String(valor)];
    }
    const primerMensaje = Object.values(fieldErrors)[0]?.[0];
    if (primerMensaje) {
      return new ApiError(primerMensaje, status, fieldErrors);
    }
  }

  if (status === 403) {
    return new ApiError("No tienes permisos para realizar esta acción.", status);
  }
  if (status === 404) {
    return new ApiError("El recurso solicitado no existe.", status);
  }

  return new ApiError("Ocurrió un error inesperado al comunicarse con el servidor.", status);
}

async function request<T>(baseUrl: string, path: string, options: RequestOptions = {}): Promise<T> {
  const { token, headers, body, ...rest } = options;

  const finalHeaders: Record<string, string> = { ...headers };
  if (body !== undefined && !finalHeaders["Content-Type"]) {
    finalHeaders["Content-Type"] = "application/json";
  }
  if (token) {
    finalHeaders["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, { ...rest, body, headers: finalHeaders });
  } catch {
    throw new ApiError(
      "No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.",
      0,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const data = parseJsonSafe(text);

  if (!response.ok) {
    throw buildApiError(response.status, data);
  }

  return data as T;
}

export function djangoRequest<T>(path: string, options?: RequestOptions): Promise<T> {
  return request<T>(DJANGO_API_URL, path, options);
}

export function fastapiRequest<T>(path: string, options?: RequestOptions): Promise<T> {
  return request<T>(FASTAPI_API_URL, path, options);
}

/**
 * Variante para respuestas binarias (el PDF de Inventario), con el mismo
 * manejo de errores que `fastapiRequest`.
 */
export async function fastapiBlobRequest(path: string, options: RequestOptions = {}): Promise<Blob> {
  const { token, headers } = options;
  const finalHeaders: Record<string, string> = { ...headers };
  if (token) {
    finalHeaders["Authorization"] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${FASTAPI_API_URL}${path}`, { headers: finalHeaders });
  } catch {
    throw new ApiError(
      "No se pudo conectar con el servidor. Verifica que el backend esté en ejecución.",
      0,
    );
  }

  if (!response.ok) {
    const text = await response.text();
    throw buildApiError(response.status, parseJsonSafe(text));
  }

  return response.blob();
}
