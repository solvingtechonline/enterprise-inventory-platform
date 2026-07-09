export interface InventarioRegistro {
  id: number;
  empresa_nit: string;
  producto_codigo: string;
  cantidad: number;
  actualizado_en: string | null;
}

export interface InventarioRegistrarInput {
  empresa_nit: string;
  producto_codigo: string;
  cantidad: number;
}
