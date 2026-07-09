/**
 * Configuración base de las APIs consumidas por el frontend.
 *
 * Next.js no asume responsabilidades de backend: solo consume las
 * APIs de Django y FastAPI.
 *
 * Los clientes concretos (fetchers, hooks) se implementarán junto con
 * cada vista funcional.
 */

export const DJANGO_API_URL =
  process.env.NEXT_PUBLIC_DJANGO_API_URL ?? "http://localhost:8000/api";

export const FASTAPI_API_URL =
  process.env.NEXT_PUBLIC_FASTAPI_API_URL ?? "http://localhost:8001";
