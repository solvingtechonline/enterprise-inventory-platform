import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import type { Empresa } from "../../lib/types/empresa";
import type { Producto } from "../../lib/types/producto";

interface Props {
  productos: Producto[];
  empresas: Empresa[];
  onVerDetalle: (producto: Producto) => void;
  onEditar: (producto: Producto) => void;
  onEliminar: (producto: Producto) => void;
}

function nombreEmpresa(empresas: Empresa[], nit: string): string {
  return empresas.find((empresa) => empresa.nit === nit)?.nombre ?? nit;
}

export function ProductoTable({ productos, empresas, onVerDetalle, onEditar, onEliminar }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-xs">
      {/* `overflow-x-auto` deja que la tabla desplace horizontalmente en
          pantallas angostas en vez de deformarse: no cambia el diseño en
          desktop, solo evita que se rompa en mobile. */}
      <div className="overflow-x-auto">
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
                  <p className="max-w-[220px] truncate font-medium text-ink" title={producto.nombre}>
                    {producto.nombre}
                  </p>
                  {producto.caracteristicas && (
                    <p
                      className="mt-0.5 max-w-[220px] truncate text-xs text-ink-muted"
                      title={producto.caracteristicas}
                    >
                      {producto.caracteristicas}
                    </p>
                  )}
                </td>
                <td className="px-4 py-3 text-ink-muted">
                  <span className="block max-w-[180px] truncate" title={nombreEmpresa(empresas, producto.empresa)}>
                    {nombreEmpresa(empresas, producto.empresa)}
                  </span>
                </td>
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
                    <Button variante="texto" tamano="sm" onClick={() => onVerDetalle(producto)}>
                      Ver detalle
                    </Button>
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
    </div>
  );
}
