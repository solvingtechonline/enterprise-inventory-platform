"""
Objeto de valor: Cantidad.

Encapsula la regla de negocio de que ninguna cantidad de inventario
puede ser negativa. Inmutable por diseño (frozen dataclass).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cantidad:
    valor: int

    def __post_init__(self) -> None:
        if not isinstance(self.valor, int) or isinstance(self.valor, bool):
            raise ValueError("La cantidad debe ser un número entero.")
        if self.valor < 0:
            raise ValueError("La cantidad en inventario no puede ser negativa.")

    def sumar(self, unidades: int) -> Cantidad:
        return Cantidad(self.valor + unidades)

    def __int__(self) -> int:
        return self.valor
