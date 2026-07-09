export type Moneda = "COP" | "USD" | "EUR";

export const MONEDAS: Moneda[] = ["COP", "USD", "EUR"];

export const ETIQUETA_MONEDA: Record<Moneda, string> = {
  COP: "COP — Peso colombiano",
  USD: "USD — Dólar estadounidense",
  EUR: "EUR — Euro",
};

export interface Precio {
  moneda: Moneda;
  valor: number;
}

export interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  caracteristicas: string;
  empresa: string; // NIT de la empresa
  precios: Precio[];
  creado_en?: string;
  actualizado_en?: string;
}

export interface ProductoInput {
  codigo: string;
  nombre: string;
  caracteristicas: string;
  empresa: string;
  precios: Precio[];
}
