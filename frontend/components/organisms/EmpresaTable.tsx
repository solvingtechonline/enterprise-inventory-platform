import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import type { Empresa } from "../../lib/types/empresa";

interface Props {
  empresas: Empresa[];
  puedeEditar: boolean;
  onEditar: (empresa: Empresa) => void;
  onEliminar: (empresa: Empresa) => void;
}

export function EmpresaTable({ empresas, puedeEditar, onEditar, onEliminar }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-xs">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface-muted text-xs uppercase tracking-wide text-ink-muted">
          <tr>
            <th className="px-4 py-3 font-medium">NIT</th>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">Dirección</th>
            <th className="px-4 py-3 font-medium">Teléfono</th>
            {puedeEditar && <th className="px-4 py-3 font-medium text-right">Acciones</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {empresas.map((empresa) => (
            <tr key={empresa.nit} className="transition-colors hover:bg-surface-muted/60">
              <td className="px-4 py-3">
                <Badge tono="neutro">{empresa.nit}</Badge>
              </td>
              <td className="px-4 py-3 font-medium text-ink">{empresa.nombre}</td>
              <td className="px-4 py-3 text-ink-muted">{empresa.direccion}</td>
              <td className="px-4 py-3 font-mono text-ink-muted">{empresa.telefono}</td>
              {puedeEditar && (
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-2">
                    <Button variante="texto" tamano="sm" onClick={() => onEditar(empresa)}>
                      Editar
                    </Button>
                    <Button
                      variante="texto"
                      tamano="sm"
                      onClick={() => onEliminar(empresa)}
                      className="!text-danger hover:!text-danger"
                    >
                      Eliminar
                    </Button>
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
