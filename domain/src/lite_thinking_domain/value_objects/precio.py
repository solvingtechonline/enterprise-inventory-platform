"""
Objeto de valor: Precio.

Encapsula la regla de negocio de que ningún precio de un Producto puede
ser negativo. Inmutable por diseño (frozen dataclass), igual que
Cantidad y Nit.

`PRECIO_MINIMO` es la única fuente de verdad del límite: tanto el
modelo de Django (validación a nivel de ORM/base de datos) como el
serializer (validación a nivel de API) deben derivar de esta constante
o de esta clase, en vez de reimplementar el límite cada uno por su
lado.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

PRECIO_MINIMO = Decimal("0")


@dataclass(frozen=True)
class Precio:
    """Precio de un Producto en una moneda determinada."""

    valor: Decimal

    def __post_init__(self) -> None:
        try:
            valor_decimal = (
                self.valor
                if isinstance(self.valor, Decimal)
                else Decimal(str(self.valor))
            )
        except (InvalidOperation, TypeError):
            raise ValueError("El precio debe ser un valor numérico válido.")
        if valor_decimal < PRECIO_MINIMO:
            raise ValueError("El precio de un producto no puede ser negativo.")
        object.__setattr__(self, "valor", valor_decimal)

    def __str__(self) -> str:
        return str(self.valor)
