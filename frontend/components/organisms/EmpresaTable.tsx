import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import type { Empresa } from "../../lib/types/empresa";

interface Props {
  empresas: Empresa[];
  puedeEditar: boolean;
  onVerDetalle: (empresa: Empresa) => void;
  onEditar: (empresa: Empresa) => void;
  onEliminar: (empresa: Empresa) => void;
}

export function EmpresaTable({ empresas, puedeEditar, onVerDetalle, onEditar, onEliminar }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-xs">
      {/* `overflow-x-auto` deja que la tabla desplace horizontalmente en
          pantallas angostas en vez de deformarse: no cambia el diseño en
          desktop, solo evita que se rompa en mobile. */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-muted text-xs uppercase tracking-wide text-ink-muted">
            <tr>
              <th className="px-4 py-3 font-medium">NIT</th>
              <th className="px-4 py-3 font-medium">Nombre</th>
              <th className="px-4 py-3 font-medium">Dirección</th>
              <th className="px-4 py-3 font-medium">Teléfono</th>
              <th className="px-4 py-3 font-medium text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {empresas.map((empresa) => (
              <tr key={empresa.nit} className="transition-colors hover:bg-surface-muted/60">
                <td className="px-4 py-3">
                  <Badge tono="neutro">{empresa.nit}</Badge>
                </td>
                <td className="px-4 py-3 font-medium text-ink">
                  <span className="block max-w-[220px] truncate" title={empresa.nombre}>
                    {empresa.nombre}
                  </span>
                </td>
                <td className="px-4 py-3 text-ink-muted">
                  <span className="block max-w-[240px] truncate" title={empresa.direccion}>
                    {empresa.direccion}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-ink-muted">{empresa.telefono}</td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-2">
                    <Button variante="texto" tamano="sm" onClick={() => onVerDetalle(empresa)}>
                      Ver detalle
                    </Button>
                    {puedeEditar && (
                      <>
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
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
