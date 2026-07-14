import { Select } from "../atoms/Select";
import { Input } from "../atoms/Input";
import { Button } from "../atoms/Button";
import { ETIQUETA_MONEDA, MONEDAS, type Precio } from "../../lib/types/producto";

interface Props {
  precio: Precio;
  index: number;
  puedeQuitar: boolean;
  /** Valor máximo aceptado (ver PRECIO_VALOR_MAXIMO en ProductoFormModal, derivado del DecimalField del backend). */
  max?: number;
  onChange: (index: number, precio: Precio) => void;
  onQuitar: (index: number) => void;
}

export function PrecioRow({ precio, index, puedeQuitar, max, onChange, onQuitar }: Props) {
  return (
    <div className="flex items-start gap-2">
      <div className="w-44">
        <Select
          aria-label="Moneda"
          value={precio.moneda}
          onChange={(event) =>
            onChange(index, { ...precio, moneda: event.target.value as Precio["moneda"] })
          }
        >
          {MONEDAS.map((moneda) => (
            <option key={moneda} value={moneda}>
              {ETIQUETA_MONEDA[moneda]}
            </option>
          ))}
        </Select>
      </div>
      <div className="flex-1">
        <Input
          aria-label="Valor"
          mono
          type="number"
          min="0"
          max={max}
          step="0.01"
          placeholder="0.00"
          value={Number.isNaN(precio.valor) ? "" : precio.valor}
          onChange={(event) =>
            onChange(index, { ...precio, valor: event.target.valueAsNumber })
          }
        />
      </div>
      <Button
        type="button"
        variante="texto"
        tamano="sm"
        onClick={() => onQuitar(index)}
        disabled={!puedeQuitar}
        aria-label="Quitar moneda"
      >
        Quitar
      </Button>
    </div>
  );
}
