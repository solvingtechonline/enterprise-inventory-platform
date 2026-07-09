export interface Empresa {
  nit: string;
  nombre: string;
  direccion: string;
  telefono: string;
  creado_en?: string;
  actualizado_en?: string;
}

export type EmpresaInput = Pick<Empresa, "nit" | "nombre" | "direccion" | "telefono">;
