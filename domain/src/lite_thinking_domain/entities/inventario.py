"""
Entidad de dominio: Inventario.

Representa la existencia de un Producto (identificado por su código,
único a nivel de sistema) dentro del Inventario de una Empresa
(identificada por su NIT). Es una entidad pura: no conoce Django,
FastAPI, SQLAlchemy ni HTTP.

La identidad de negocio de un registro de inventario es la combinación
(empresa_nit, producto_codigo): una empresa no puede tener dos registros
de inventario distintos para el mismo producto.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from lite_thinking_domain.value_objects.cantidad import Cantidad


@dataclass
class Inventario:
    """Registro de inventario de un Producto para una Empresa."""

    empresa_nit: str
    producto_codigo: str
    cantidad: Cantidad
    id: int | None = None
    actualizado_en: datetime | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.empresa_nit or not self.empresa_nit.strip():
            raise ValueError("El NIT de la empresa es obligatorio.")
        if not self.producto_codigo or not self.producto_codigo.strip():
            raise ValueError("El código del producto es obligatorio.")
        # Garantiza que 'cantidad' siempre sea el objeto de valor, incluso
        # si el llamador pasó un entero crudo.
        if not isinstance(self.cantidad, Cantidad):
            self.cantidad = Cantidad(int(self.cantidad))

    def incrementar(self, unidades: int) -> None:
        """Suma unidades al registro existente (alta de más stock del mismo producto)."""
        self.cantidad = self.cantidad.sumar(unidades)

    def establecer_cantidad(self, nueva_cantidad: int) -> None:
        """Reemplaza la cantidad actual por una nueva (ej. corrección de stock)."""
        self.cantidad = Cantidad(nueva_cantidad)
