import { Badge } from "../atoms/Badge";
import { Button } from "../atoms/Button";
import type { InventarioRegistro } from "../../lib/types/inventario";
import type { Producto } from "../../lib/types/producto";

interface Props {
  registros: InventarioRegistro[];
  productos: Producto[];
  onVerDetalle: (registro: InventarioRegistro) => void;
  onEditar: (registro: InventarioRegistro) => void;
  onEliminar: (registro: InventarioRegistro) => void;
}

function nombreProducto(productos: Producto[], codigo: string): string {
  return productos.find((producto) => producto.codigo === codigo)?.nombre ?? "-";
}

function formatearFecha(fecha: string | null): string {
  if (!fecha) return "-";
  return new Date(fecha).toLocaleString("es-CO", { dateStyle: "medium", timeStyle: "short" });
}

export function InventarioTable({ registros, productos, onVerDetalle, onEditar, onEliminar }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-xs">
      {/* `overflow-x-auto` deja que la tabla desplace horizontalmente en
          pantallas angostas en vez de deformarse: no cambia el diseño en
          desktop, solo evita que se rompa en mobile. */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-muted text-xs uppercase tracking-wide text-ink-muted">
            <tr>
              <th className="px-4 py-3 font-medium">Producto</th>
              <th className="px-4 py-3 font-medium">Cantidad</th>
              <th className="px-4 py-3 font-medium">Actualizado</th>
              <th className="px-4 py-3 font-medium text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {registros.map((registro) => (
              <tr key={registro.id} className="transition-colors hover:bg-surface-muted/60">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Badge tono="neutro">{registro.producto_codigo}</Badge>
                    <span
                      className="block max-w-[200px] truncate text-ink"
                      title={nombreProducto(productos, registro.producto_codigo)}
                    >
                      {nombreProducto(productos, registro.producto_codigo)}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 font-mono font-medium text-ink">{registro.cantidad}</td>
                <td className="px-4 py-3 text-ink-muted">{formatearFecha(registro.actualizado_en)}</td>
                <td className="px-4 py-3">
                  <div className="flex justify-end gap-2">
                    <Button variante="texto" tamano="sm" onClick={() => onVerDetalle(registro)}>
                      Ver detalle
                    </Button>
                    <Button variante="texto" tamano="sm" onClick={() => onEditar(registro)}>
                      Corregir cantidad
                    </Button>
                    <Button
                      variante="texto"
                      tamano="sm"
                      onClick={() => onEliminar(registro)}
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
