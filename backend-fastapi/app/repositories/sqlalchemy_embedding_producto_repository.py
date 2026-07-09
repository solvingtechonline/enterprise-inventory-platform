"""
Adaptador de infraestructura: implementa el puerto de dominio
`EmbeddingProductoRepository` usando SQLAlchemy + pgvector sobre la
tabla `producto_embedding`.

Mismo patrón que `SQLAlchemyInventarioRepository`: es la única pieza
que traduce entre la entidad de dominio `EmbeddingProducto` (pura) y
el modelo físico `ProductoEmbeddingModel` (SQLAlchemy). Ningún otro
módulo debe conocer SQLAlchemy/pgvector más allá de este archivo y
`app.models.producto_embedding`.

Nota sobre `buscar_similares` (búsqueda semántica): usa el
operador de distancia coseno de pgvector (`<=>`, expuesto por
`Vector.cosine_distance`) tanto para ordenar como para devolver el
valor de distancia de cada fila. Este adaptador no decide qué tan
lejos es "demasiado lejos" — eso es una regla de negocio que vive en
`EmbeddingProductoService.buscar_semanticamente` (dominio), no en esta
consulta SQL. Este archivo solo traduce entre pgvector y el puerto de
dominio.
"""

from __future__ import annotations

from lite_thinking_domain.entities.embedding_producto import EmbeddingProducto
from lite_thinking_domain.repositories.embedding_producto_repository import (
    EmbeddingProductoRepository,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.producto_embedding import ProductoEmbeddingModel


def _a_entidad(modelo: ProductoEmbeddingModel) -> EmbeddingProducto:
    return EmbeddingProducto(
        id=modelo.id,
        producto_codigo=modelo.producto_codigo,
        texto_fuente=modelo.texto_fuente,
        vector=list(modelo.vector),
        actualizado_en=modelo.actualizado_en,
    )


class SQLAlchemyEmbeddingProductoRepository(EmbeddingProductoRepository):
    """Implementación concreta del puerto de dominio, vía SQLAlchemy + pgvector."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def guardar(self, embedding: EmbeddingProducto) -> EmbeddingProducto:
        if embedding.id is not None:
            modelo = self._db.get(ProductoEmbeddingModel, embedding.id)
            if modelo is None:
                raise ValueError(f"No existe el embedding id={embedding.id}.")
            modelo.texto_fuente = embedding.texto_fuente
            modelo.vector = embedding.vector
        else:
            modelo = ProductoEmbeddingModel(
                producto_codigo=embedding.producto_codigo,
                texto_fuente=embedding.texto_fuente,
                vector=embedding.vector,
            )
            self._db.add(modelo)

        self._db.commit()
        self._db.refresh(modelo)
        return _a_entidad(modelo)

    def buscar_por_producto(self, producto_codigo: str) -> EmbeddingProducto | None:
        stmt = select(ProductoEmbeddingModel).where(
            ProductoEmbeddingModel.producto_codigo == producto_codigo
        )
        modelo = self._db.execute(stmt).scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    def buscar_similares(
        self, vector: list[float], limite: int = 5
    ) -> list[tuple[EmbeddingProducto, float]]:
        distancia = ProductoEmbeddingModel.vector.cosine_distance(vector).label(
            "distancia"
        )
        stmt = (
            select(ProductoEmbeddingModel, distancia)
            .order_by(distancia)
            .limit(limite)
        )
        filas = self._db.execute(stmt).all()
        return [(_a_entidad(modelo), float(dist)) for modelo, dist in filas]

    def eliminar(self, producto_codigo: str) -> bool:
        stmt = select(ProductoEmbeddingModel).where(
            ProductoEmbeddingModel.producto_codigo == producto_codigo
        )
        modelo = self._db.execute(stmt).scalar_one_or_none()
        if modelo is None:
            return False
        self._db.delete(modelo)
        self._db.commit()
        return True
