"use client";

import { useState } from "react";

import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import { Input } from "../atoms/Input";
import { Spinner } from "../atoms/Spinner";
import { Alert } from "../molecules/Alert";
import { EmptyState } from "../molecules/EmptyState";
import { buscarProductosSemantico } from "../../lib/api/ia";
import { ApiError } from "../../lib/api/http";
import type { ProductoResultadoBusqueda } from "../../lib/types/ia";

// El endpoint `GET /api/ia/buscar` (backend-fastapi/app/api/ia.py) no
// impone un tope de longitud a `consulta`, pero es una búsqueda en
// lenguaje natural, no un campo de texto libre: una consulta larguísima
// solo dispara una llamada de generación de embeddings más costosa sin
// aportar precisión. 200 caracteres es un tope de negocio/UX razonable
// para una frase de búsqueda.
const CONSULTA_MAX_LENGTH = 200;

interface Props {
  token: string;
  /** Reutiliza el filtro por empresa ya existente en `productos/page.tsx` para ubicar el resultado en la tabla. */
  onFiltrarEmpresa?: (empresaNit: string) => void;
}

/**
 * Panel de búsqueda semántica (agente de IA con pgvector) para la vista
 * de Productos. Autocontenido: maneja su propio estado de consulta,
 * carga y error, igual que el resto de organismos de esta carpeta.
 *
 * Vive dentro de `AuthGate` en `app/productos/page.tsx`: el endpoint
 * `GET /api/ia/buscar` ya exige rol Administrador, así que no agrega
 * lógica de permisos propia.
 */
export function BusquedaSemanticaProductos({ token, onFiltrarEmpresa }: Props) {
  const [abierto, setAbierto] = useState(false);
  const [consulta, setConsulta] = useState("");
  const [resultados, setResultados] = useState<ProductoResultadoBusqueda[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const buscar = async () => {
    const texto = consulta.trim();
    if (!texto) return;

    setIsLoading(true);
    setError(null);
    try {
      const respuesta = await buscarProductosSemantico(texto, token);
      setResultados(respuesta.resultados);
    } catch (err) {
      setResultados(null);
      setError(
        err instanceof ApiError
          ? err.message
          : "No se pudo completar la búsqueda semántica.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mb-4 rounded-lg border border-border bg-surface shadow-xs">
      <button
        type="button"
        onClick={() => setAbierto((valor) => !valor)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left
          focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent"
        aria-expanded={abierto}
      >
        <span className="flex items-center gap-2">
          <span className="font-display text-sm font-semibold text-ink">Búsqueda con IA</span>
          <Badge tono="primario">semántica</Badge>
        </span>
        <span className="text-xs text-ink-muted">{abierto ? "Ocultar" : "Buscar por descripción"}</span>
      </button>

      {abierto && (
        <div className="border-t border-border px-4 py-4">
          <p className="mb-3 text-xs text-ink-muted">
            Describe lo que buscas en lenguaje natural (ej. &ldquo;laptop para diseño gráfico&rdquo;). El
            agente compara embeddings de productos ya ingeridos y solo devuelve resultados relevantes.
          </p>

          <form
            className="flex flex-wrap items-center gap-2"
            onSubmit={(event) => {
              event.preventDefault();
              buscar();
            }}
          >
            <div className="min-w-[240px] flex-1">
              <Input
                aria-label="Consulta de búsqueda semántica"
                placeholder="Ej. teclado para oficina"
                maxLength={CONSULTA_MAX_LENGTH}
                value={consulta}
                onChange={(event) => setConsulta(event.target.value)}
              />
            </div>
            <Button type="submit" tamano="sm" isLoading={isLoading} disabled={!consulta.trim()}>
              Buscar
            </Button>
          </form>

          <div className="mt-4">
            {error && (
              <div className="mb-3">
                <Alert tono="peligro" onDismiss={() => setError(null)}>
                  {error}
                </Alert>
              </div>
            )}

            {isLoading && <Spinner label="Consultando al agente de IA…" />}

            {!isLoading && resultados && resultados.length === 0 && (
              <EmptyState
                title="Sin resultados relevantes"
                description="Ningún producto ingerido se relaciona semánticamente con esa consulta."
              />
            )}

            {!isLoading && resultados && resultados.length > 0 && (
              <ul className="divide-y divide-border overflow-hidden rounded-lg border border-border">
                {resultados.map((resultado) => (
                  <li
                    key={resultado.producto_codigo}
                    className="flex items-center justify-between gap-3 px-4 py-3 text-sm transition-colors hover:bg-surface-muted/60"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <Badge tono="neutro">{resultado.producto_codigo}</Badge>
                        <span className="truncate text-ink">{resultado.nombre ?? "-"}</span>
                      </div>
                      {resultado.caracteristicas && (
                        <p className="mt-1 truncate text-xs text-ink-muted">
                          {resultado.caracteristicas}
                        </p>
                      )}
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <Badge tono="exito">{Math.round(resultado.similitud * 100)}% similar</Badge>
                      {onFiltrarEmpresa && resultado.empresa_nit && (
                        <Button
                          type="button"
                          variante="texto"
                          tamano="sm"
                          onClick={() => onFiltrarEmpresa(resultado.empresa_nit!)}
                        >
                          Ver en tabla
                        </Button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
