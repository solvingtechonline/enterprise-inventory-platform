"""
Esquemas Pydantic del agente de IA (ingesta de embeddings).

Son responsabilidad exclusiva de FastAPI (capa de infraestructura/API):
el dominio no conoce Pydantic, solo la entidad `EmbeddingProducto` pura
(mismo criterio que `app.schemas.inventario`).
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class EmbeddingIngestarInput(BaseModel):
    """Body para generar (o regenerar) el embedding vigente de un producto."""

    empresa_nit: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description=(
            "NIT de la empresa a la que pertenece el producto (se usa para "
            "consultarlo en la API de Django, que no expone búsqueda por "
            "código de producto de forma directa)."
        ),
    )
    producto_codigo: str = Field(
        ..., min_length=1, max_length=50, description="Código único del producto."
    )


class EmbeddingRead(BaseModel):
    """
    Confirmación del embedding vigente generado y guardado.

    No expone el vector completo (1536 floats) en la respuesta HTTP;
    solo su dimensión, como evidencia de que se generó correctamente.
    """

    producto_codigo: str
    texto_fuente: str
    dimension: int
    actualizado_en: datetime | None = None


class ProductoResultadoBusqueda(BaseModel):
    """
    Un producto devuelto por la búsqueda semántica, ya enriquecido con
    sus datos de negocio (Django) además de la distancia/similitud
    calculada por el dominio.
    """

    producto_codigo: str
    nombre: str | None = None
    caracteristicas: str | None = None
    empresa_nit: str | None = None
    distancia: float
    similitud: float


class BusquedaSemanticaRead(BaseModel):
    """Respuesta del endpoint de búsqueda semántica."""

    consulta: str
    resultados: list[ProductoResultadoBusqueda]
