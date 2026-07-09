"""
Entidad de dominio: Producto.

Representa un Producto del negocio: Código, Nombre, Características,
Precio en varias monedas, Empresa. Entidad pura: no conoce Django,
FastAPI, SQLAlchemy ni HTTP.

El precio en cada moneda se valida mediante el objeto de valor Precio
(no puede ser negativo). La entidad admite varios precios (uno por
moneda), igual que el modelo PrecioProducto de Django.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from lite_thinking_domain.value_objects.precio import Precio


@dataclass
class Producto:
    """Entidad Producto. Cada precio se valida mediante el objeto de valor Precio."""

    codigo: str
    nombre: str
    empresa_nit: str
    precios: list[Precio] = field(default_factory=list)
    caracteristicas: str = ""

    def __post_init__(self) -> None:
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código del producto es obligatorio.")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del producto es obligatorio.")
        if not self.empresa_nit or not str(self.empresa_nit).strip():
            raise ValueError("El producto debe estar asociado a una empresa (NIT).")
        # Garantiza que cada precio sea el objeto de valor, incluso si el
        # llamador pasó números crudos.
        self.precios = [
            precio if isinstance(precio, Precio) else Precio(precio)
            for precio in self.precios
        ]
