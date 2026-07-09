/**
 * Tipos del agente de IA (búsqueda semántica de productos).
 * Espejo de `backend-fastapi/app/schemas/ia.py`.
 */

export interface ProductoResultadoBusqueda {
  producto_codigo: string;
  nombre: string | null;
  caracteristicas: string | null;
  empresa_nit: string | null;
  distancia: number;
  similitud: number;
}

export interface BusquedaSemanticaRead {
  consulta: string;
  resultados: ProductoResultadoBusqueda[];
}
