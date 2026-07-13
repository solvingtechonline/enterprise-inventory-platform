import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import type { Empresa } from "../../lib/types/empresa";
import type { Producto } from "../../lib/types/producto";

interface Props {
  productos: Producto[];
  empresas: Empresa[];
  onEditar: (producto: Producto) => void;
  onEliminar: (producto: Producto) => void;
}

function nombreEmpresa(empresas: Empresa[], nit: string): string {
  return empresas.find((empresa) => empresa.nit === nit)?.nombre ?? nit;
}

export function ProductoTable({ productos, empresas, onEditar, onEliminar }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-xs">
      <table className="w-full text-left text-sm">
        <thead className="bg-surface-muted text-xs uppercase tracking-wide text-ink-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Código</th>
            <th className="px-4 py-3 font-medium">Nombre</th>
            <th className="px-4 py-3 font-medium">Empresa</th>
            <th className="px-4 py-3 font-medium">Precios</th>
            <th className="px-4 py-3 font-medium text-right">Acciones</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {productos.map((producto) => (
            <tr key={producto.id} className="align-top transition-colors hover:bg-surface-muted/60">
              <td className="px-4 py-3">
                <Badge tono="neutro">{producto.codigo}</Badge>
              </td>
              <td className="px-4 py-3">
                <p className="font-medium text-ink">{producto.nombre}</p>
                {producto.caracteristicas && (
                  <p className="mt-0.5 max-w-xs text-xs text-ink-muted">{producto.caracteristicas}</p>
                )}
              </td>
              <td className="px-4 py-3 text-ink-muted">{nombreEmpresa(empresas, producto.empresa)}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {producto.precios.map((precio) => (
                    <span
                      key={precio.moneda}
                      className="font-mono text-xs text-ink-muted"
                    >
                      {precio.moneda} {precio.valor.toLocaleString("es-CO", { minimumFractionDigits: 2 })}
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-2">
                  <Button variante="texto" tamano="sm" onClick={() => onEditar(producto)}>
                    Editar
                  </Button>
                  <Button
                    variante="texto"
                    tamano="sm"
                    onClick={() => onEliminar(producto)}
                    className="!text-danger hover:!text-danger"
                  >
                    Eliminar
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
