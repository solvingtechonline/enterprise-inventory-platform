"""
Entidad de dominio: EmbeddingProducto.

Representa el embedding vectorial vigente de un Producto, para el
agente de IA con búsqueda semántica sobre pgvector. Entidad pura: el
vector es una lista de float; no conoce pgvector, SQLAlchemy ni ningún
driver de infraestructura.

La identidad de negocio es el producto_codigo: cada producto tiene un
único embedding vigente (volver a generarlo reemplaza el vector
anterior, no crea un duplicado — mismo criterio que Inventario con
empresa_nit + producto_codigo).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EmbeddingProducto:
    """Embedding vectorial vigente de un Producto."""

    producto_codigo: str
    texto_fuente: str
    vector: list[float]
    id: int | None = None
    actualizado_en: datetime | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.producto_codigo or not self.producto_codigo.strip():
            raise ValueError("El código del producto es obligatorio.")
        if not self.texto_fuente or not self.texto_fuente.strip():
            raise ValueError("El texto fuente del embedding es obligatorio.")
        if not self.vector:
            raise ValueError("El vector del embedding no puede estar vacío.")

    def reemplazar_vector(self, nuevo_vector: list[float], nuevo_texto_fuente: str) -> None:
        """Actualiza el embedding vigente (ej. tras editar el producto)."""
        if not nuevo_vector:
            raise ValueError("El vector del embedding no puede estar vacío.")
        if not nuevo_texto_fuente or not nuevo_texto_fuente.strip():
            raise ValueError("El texto fuente del embedding es obligatorio.")
        self.vector = nuevo_vector
        self.texto_fuente = nuevo_texto_fuente
