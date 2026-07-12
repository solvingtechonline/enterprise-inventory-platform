"""
Modelo SQLAlchemy de la tabla `producto_embedding`.

Almacena el embedding vectorial vigente de cada Producto, para el
agente de IA con búsqueda semántica sobre pgvector. FastAPI/SQLAlchemy
es dueño exclusivo de esta tabla, igual que de `inventario`. Reutiliza
el mismo `Base`/engine de `app.db.session` que ya usa InventarioModel:
no se abre una conexión nueva a PostgreSQL.

No se declara una ForeignKey real hacia la tabla `producto`
(administrada por el ORM de Django): se guarda solo la referencia por
valor (producto_codigo), mismo criterio que InventarioModel con
`empresa_nit`/`producto_codigo`.

La dimensión del vector (1536) corresponde al proveedor de embeddings
elegido para el proyecto. Ver docs/agente_ia_decision_proveedor.md.
"""

from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

# Dimensión del vector: text-embedding-3-small (OpenAI), proveedor elegido
# para este proyecto (ver docs/agente_ia_decision_proveedor.md).
DIMENSION_EMBEDDING = 1536


class ProductoEmbeddingModel(Base):
    """Fila física de la tabla `producto_embedding`."""

    __tablename__ = "producto_embedding"
    __table_args__ = (
        UniqueConstraint("producto_codigo", name="uq_producto_embedding_codigo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto_codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    texto_fuente: Mapped[str] = mapped_column(Text, nullable=False)
    vector: Mapped[list[float]] = mapped_column(Vector(DIMENSION_EMBEDDING), nullable=False)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
