"""
Entidad de dominio: ResultadoBusquedaProducto.

Representa un producto devuelto por la búsqueda semántica del agente de
IA, ya evaluado contra la regla de negocio de "qué es un resultado
relevante" (ver `EmbeddingProductoService.UMBRAL_DISTANCIA_RELEVANTE`).

Pura: no conoce pgvector, SQLAlchemy ni HTTP. Se construye a partir de
la distancia coseno que devuelve el puerto de persistencia
(`EmbeddingProductoRepository.buscar_similares`), pero la entidad en sí
no sabe qué motor de base de datos la calculó.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoBusquedaProducto:
    """Un producto candidato de la búsqueda semántica, con su distancia."""

    producto_codigo: str
    texto_fuente: str
    distancia: float

    def __post_init__(self) -> None:
        if not self.producto_codigo or not self.producto_codigo.strip():
            raise ValueError("El código del producto es obligatorio.")
        if self.distancia < 0:
            raise ValueError("La distancia no puede ser negativa.")

    @property
    def similitud(self) -> float:
        """
        Similitud coseno equivalente (pgvector's `cosine_distance` =
        1 - similitud_coseno). Se expone como conveniencia para la capa
        de presentación (ej. mostrar un porcentaje), no para decidir
        relevancia: esa decisión ya se tomó en el dominio antes de que
        este resultado exista (ver `EmbeddingProductoService.buscar_semanticamente`).
        """
        return 1 - self.distancia
